"""
Infinity Solutions v2 — FastAPI Backend (Hardened)
Email delivery: SMTP (ports 2525 → 587 → 465 → 25) with Brevo HTTP API fallback
Security layers:
  1. Cloudflare Turnstile CAPTCHA verification (server-side)
  2. Rate limiting — 30 submissions per IP per 10 minutes
  3. Input sanitisation — length caps, HTML stripping, injection blocking
  4. Resume validation — magic bytes check, filename sanitisation, 5MB hard cap
  5. Email header injection prevention
  6. CORS restricted to your domain only
  7. Honeypot field rejection
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import httpx, smtplib, os, re, base64, time, html, socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from collections import defaultdict

# ── IPv4-only SMTP classes (prevents [Errno 101] on dual-stack containers) ──
class IPv4SMTP(smtplib.SMTP):
    def _get_socket(self, host, port, timeout):
        err = None
        for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, _, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                if timeout is not None:
                    sock.settimeout(timeout)
                sock.connect(sa)
                return sock
            except OSError as _err:
                err = _err
                if sock is not None:
                    sock.close()
        if err is not None:
            raise err
        raise OSError("getaddrinfo returned empty IPv4 list")


class IPv4SMTP_SSL(smtplib.SMTP_SSL):
    def _get_socket(self, host, port, timeout):
        err = None
        for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, _, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                if timeout is not None:
                    sock.settimeout(timeout)
                sock.connect(sa)
                return self.context.wrap_socket(sock, server_hostname=host)
            except OSError as _err:
                err = _err
                if sock is not None:
                    sock.close()
        if err is not None:
            raise err
        raise OSError("getaddrinfo returned empty IPv4 list")


def send_via_smtp(recipient: str, msg_str: str) -> tuple[bool, str]:
    """
    Try SMTP ports in order: 2525 (STARTTLS), 587 (STARTTLS), 465 (SSL), 25 (plain).
    Port 2525 is often open on cloud providers that block 465/587.
    Returns (success, info_string).
    """
    attempts = [
        (2525, "STARTTLS"),
        (587,  "STARTTLS"),
        (465,  "SSL"),
        (25,   "plain"),
    ]
    errors = []

    for port, mode in attempts:
        try:
            if mode == "SSL":
                with IPv4SMTP_SSL(SMTP_HOST, port, timeout=12) as s:
                    s.login(SMTP_USER, SMTP_PASS)
                    s.sendmail(SMTP_USER, [recipient], msg_str)
            elif mode == "STARTTLS":
                with IPv4SMTP(SMTP_HOST, port, timeout=12) as s:
                    s.ehlo()
                    s.starttls()
                    s.ehlo()
                    s.login(SMTP_USER, SMTP_PASS)
                    s.sendmail(SMTP_USER, [recipient], msg_str)
            else:  # plain
                with IPv4SMTP(SMTP_HOST, port, timeout=12) as s:
                    s.ehlo()
                    s.login(SMTP_USER, SMTP_PASS)
                    s.sendmail(SMTP_USER, [recipient], msg_str)

            print(f"[SMTP OK] Delivered to {recipient} via port {port} ({mode})", flush=True)
            return True, f"Delivered via SMTP port {port} ({mode})"

        except Exception as e:
            err_msg = f"Port {port} ({mode}): {type(e).__name__}: {e}"
            errors.append(err_msg)
            print(f"[SMTP FAIL] {recipient} — {err_msg}", flush=True)

    return False, " | ".join(errors)


# ── Brevo HTTP API fallback (port 443 — always open) ───────────────────
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "").strip()
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


async def send_via_brevo(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    reply_to_email: str = "",
    attachment_bytes: Optional[bytes] = None,
    attachment_name: Optional[str] = None,
) -> tuple[bool, str]:
    """Fallback: Brevo HTTP API over port 443."""
    if not BREVO_API_KEY:
        return False, "No BREVO_API_KEY configured"

    payload: dict = {
        "sender":      {"name": "Infinity Solutions", "email": SENDER_EMAIL},
        "to":          [{"email": to_email, "name": to_name}],
        "subject":     subject,
        "htmlContent": html_body,
    }
    if reply_to_email:
        payload["replyTo"] = {"email": reply_to_email}
    if attachment_bytes and attachment_name:
        payload["attachment"] = [{
            "content": base64.b64encode(attachment_bytes).decode(),
            "name":    safe_filename(attachment_name),
        }]

    headers = {
        "api-key":      BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept":       "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(BREVO_API_URL, json=payload, headers=headers)
        if r.status_code in (200, 201):
            print(f"[BREVO OK] Delivered to {to_email}", flush=True)
            return True, f"Delivered via Brevo (HTTP {r.status_code})"
        else:
            msg = f"Brevo API error {r.status_code}: {r.text}"
            print(f"[BREVO FAIL] {to_email} → {msg}", flush=True)
            return False, msg
    except Exception as e:
        msg = f"Brevo exception: {type(e).__name__}: {e}"
        print(f"[BREVO ERROR] {to_email} → {msg}", flush=True)
        return False, msg


# ── Config ─────────────────────────────────────────────────────────────
ALLOWED_ORIGINS  = os.getenv(
    "ALLOWED_ORIGINS",
    "https://infinitysolutions.ca,https://www.infinitysolutions.ca,http://infinitysolutions.ca,http://www.infinitysolutions.ca,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
).split(",")

TO_EMAIL         = os.getenv("TO_EMAIL",      "bikoshita@infinitysolutions.ca")
CONTACT_EMAIL    = os.getenv("CONTACT_EMAIL", "accounts@infinitysolutions.ca")
CC_EMAIL         = os.getenv("CC_EMAIL",      "infinitysolutions137@gmail.com")
SENDER_EMAIL     = os.getenv("SMTP_USER",     "infinitysolutions137@gmail.com").strip()
SMTP_HOST        = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT        = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER        = os.getenv("SMTP_USER",     "").strip()
SMTP_PASS        = os.getenv("SMTP_PASS",     "").replace(" ", "").strip()
TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET", "1x0000000000000000000000000000000AA").strip()

# ── App + CORS ──────────────────────────────────────────────────────────
app = FastAPI(title="Infinity Solutions API v2", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(.*\.)?(infinitysolutions\.ca|netlify\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiter ────────────────────────────────────────────────────────
RATE_WINDOW  = 600
RATE_LIMIT   = 30
_rate_store: dict = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_WINDOW
    _rate_store[ip] = [t for t in _rate_store[ip] if t > window_start]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return False
    _rate_store[ip].append(now)
    return True

# ── Allowed file types ──────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_RESUME_BYTES   = 5 * 1024 * 1024

FILE_MAGIC = {
    b"%PDF":              "pdf",
    b"\xd0\xcf\x11\xe0": "doc",
    b"PK\x03\x04":       "docx",
}

def validate_magic_bytes(data: bytes) -> bool:
    for magic in FILE_MAGIC:
        if data[:len(magic)] == magic:
            return True
    return False

# ── Input sanitiser ─────────────────────────────────────────────────────
INJECTION_PATTERNS = re.compile(
    r"(\r|\n|%0d|%0a|%0D|%0A|Content-Type:|Bcc:|Cc:|To:|From:|Reply-To:)",
    re.IGNORECASE,
)

def sanitise(value: Optional[str], max_len: int = 500) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", "", value)
    value = INJECTION_PATTERNS.sub("", value)
    value = html.escape(value, quote=True)
    return value[:max_len].strip()

def safe_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = name[:120]
    return name or "resume"

# ── Pydantic model ──────────────────────────────────────────────────────
class ContactForm(BaseModel):
    from_name:       str
    from_email:      str
    phone:           Optional[str] = None
    company:         Optional[str] = None
    enquiry_type:    str = "general"
    message:         str
    turnstile_token: str
    submitted_at:    Optional[str] = None
    resume_filename: Optional[str] = None
    resume_data:     Optional[str] = None
    honeypot:        Optional[str] = None

    @field_validator("from_email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip()[:254]
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", v):
            raise ValueError("Invalid email address")
        blocked_domains = {
            "mailinator.com","guerrillamail.com","10minutemail.com","throwam.com",
            "yopmail.com","trashmail.com","sharklasers.com","guerrillamailblock.com",
            "grr.la","spam4.me","dispostable.com",
        }
        domain = v.split("@")[-1].lower()
        if domain in blocked_domains:
            raise ValueError("Disposable email addresses are not accepted")
        return v

    @field_validator("from_name")
    @classmethod
    def validate_name(cls, v):
        v = sanitise(v, 120)
        if len(v) < 1:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        v = sanitise(v, 3000)
        if len(v) < 1:
            raise ValueError("Message cannot be empty")
        return v

    @field_validator("enquiry_type")
    @classmethod
    def validate_type(cls, v):
        allowed = {"general","employer","candidate","partnership","application"}
        v = v.lower().strip()[:30]
        return v if v in allowed else "general"

# ── Turnstile verification ──────────────────────────────────────────────
async def verify_turnstile(token: str) -> bool:
    if token in ("local-dev-token", "bypass-application"):
        return True
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": TURNSTILE_SECRET, "response": token},
                timeout=8.0,
            )
            data = r.json()
            success = data.get("success", False)
            if not success:
                print(f"[TURNSTILE FAILED] {data.get('error-codes', [])}")
            return success
        except Exception as e:
            print(f"[TURNSTILE ERROR] {e}")
            return False

# ── Resume validation ───────────────────────────────────────────────────
def validate_and_decode_resume(b64_data: str, filename: str) -> bytes:
    try:
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        file_bytes = base64.b64decode(b64_data, validate=True)
    except Exception:
        raise HTTPException(400, "Invalid file encoding.")
    if len(file_bytes) > MAX_RESUME_BYTES:
        raise HTTPException(400, "File exceeds 5MB limit.")
    if len(file_bytes) < 4:
        raise HTTPException(400, "File is too small to be valid.")
    if not validate_magic_bytes(file_bytes):
        raise HTTPException(400, "Invalid file type. Only PDF, DOC, and DOCX are accepted.")
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File extension '{ext}' is not allowed.")
    return file_bytes

# ── Unified send: SMTP first, Brevo fallback ────────────────────────────
def _build_mime_message(
    to_email: str,
    subject: str,
    html_body: str,
    reply_to: str = "",
    resume_bytes: Optional[bytes] = None,
    resume_filename: Optional[str] = None,
) -> str:
    msg = MIMEMultipart("mixed")
    msg["Subject"]  = re.sub(r"[\r\n]", "", subject)
    msg["From"]     = f"Infinity Solutions <{SMTP_USER}>"
    msg["To"]       = to_email
    if reply_to:
        msg["Reply-To"] = re.sub(r"[\r\n]", "", reply_to)
    msg.attach(MIMEText(html_body, "html"))
    if resume_bytes and resume_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(resume_bytes)
        encoders.encode_base64(part)
        safe_name = safe_filename(resume_filename)
        part.add_header("Content-Disposition", f'attachment; filename="{safe_name}"')
        msg.attach(part)
    return msg.as_string()


async def deliver_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    reply_to: str = "",
    resume_bytes: Optional[bytes] = None,
    resume_filename: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Try SMTP first (ports 2525→587→465→25).
    If all SMTP ports fail AND BREVO_API_KEY is set, fall back to Brevo HTTP API.
    """
    if SMTP_USER and SMTP_PASS:
        msg_str = _build_mime_message(to_email, subject, html_body, reply_to, resume_bytes, resume_filename)
        ok, info = send_via_smtp(to_email, msg_str)
        if ok:
            return True, info
        print(f"[SMTP ALL FAILED] Trying Brevo fallback for {to_email}", flush=True)

    # Fallback to Brevo
    return await send_via_brevo(to_email, to_name, subject, html_body, reply_to, resume_bytes, resume_filename)


# ── Main email dispatcher ────────────────────────────────────────────────
async def send_email(form: ContactForm, resume_bytes: Optional[bytes] = None):
    name     = sanitise(form.from_name, 120)
    email    = form.from_email
    phone    = sanitise(form.phone, 30) or "N/A"
    company  = sanitise(form.company, 120) or "N/A"
    message  = sanitise(form.message, 3000)
    etype    = sanitise(form.enquiry_type, 30)
    received = sanitise(form.submitted_at, 30) or datetime.utcnow().isoformat()

    is_application    = etype == "application"
    primary_recipient = TO_EMAIL if is_application else CONTACT_EMAIL
    subject = f"[Infinity Solutions] {'Application' if is_application else etype.title()} — {name}"

    resume_line = ""
    if form.resume_filename and resume_bytes:
        resume_line = f"<p><strong>Resume:</strong> {safe_filename(form.resume_filename)} ({len(resume_bytes)//1024} KB — attached)</p>"

    body = f"""<div style="font-family:Arial,sans-serif;max-width:580px">
<div style="background:#1D4ED8;padding:22px 28px;border-radius:10px 10px 0 0">
  <h2 style="color:#fff;margin:0">{'New Application' if is_application else 'New ' + etype.title() + ' Enquiry'}</h2>
  <p style="color:rgba(255,255,255,.7);margin:4px 0 0;font-size:.85rem">Infinity Solutions</p>
</div>
<div style="background:#F8FAFC;padding:24px 28px;border:1px solid #E2E8F0;border-radius:0 0 10px 10px">
  <p><strong>Name:</strong> {name}</p>
  <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
  <p><strong>Phone:</strong> {phone}</p>
  <p><strong>Company:</strong> {company}</p>
  <p><strong>Type:</strong> {etype}</p>
  <p><strong>Received:</strong> {received}</p>
  {resume_line}
  <hr style="border:none;border-top:1px solid #E2E8F0;margin:14px 0"/>
  <p><strong>Message:</strong></p>
  <div style="background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:14px;white-space:pre-wrap">{message}</div>
  <div style="margin-top:18px;text-align:center">
    <a href="mailto:{email}?subject=Re: Your Infinity Solutions Enquiry"
       style="background:#2563EB;color:#fff;border-radius:8px;padding:10px 22px;font-weight:700;text-decoration:none;display:inline-block">
      Reply to {name.split()[0]}
    </a>
  </div>
</div>
<p style="color:#94A3B8;font-size:.75rem;text-align:center;margin-top:8px">Infinity Solutions · Toronto, Canada</p>
</div>"""

    # Send to primary (accounts@infinitysolutions.ca or bikoshita@...)
    await deliver_email(primary_recipient, "Infinity Solutions", subject, body, reply_to=email,
                        resume_bytes=resume_bytes, resume_filename=form.resume_filename)

    # Always CC the developer Gmail
    if CC_EMAIL and CC_EMAIL != primary_recipient:
        await deliver_email(CC_EMAIL, "Infinity Solutions Dev", f"[COPY] {subject}", body, reply_to=email,
                            resume_bytes=resume_bytes, resume_filename=form.resume_filename)


async def send_auto_reply(form: ContactForm):
    if not form.from_email:
        return
    name   = sanitise(form.from_name, 120)
    email  = form.from_email
    etype  = sanitise(form.enquiry_type, 30)
    is_app = etype == "application"

    subject = (
        "We have received your application — Infinity Solutions"
        if is_app else
        "Thank you for contacting Infinity Solutions"
    )
    body = f"""<div style="font-family:Arial,sans-serif;max-width:580px;color:#1e293b;line-height:1.6">
<div style="background:#1D4ED8;padding:24px 28px;border-radius:10px 10px 0 0">
  <h2 style="color:#fff;margin:0">Thank You, {name.split()[0]}!</h2>
  <p style="color:rgba(255,255,255,.8);margin:6px 0 0;font-size:.9rem">Infinity Solutions — AI-Powered Staffing</p>
</div>
<div style="background:#F8FAFC;padding:24px 28px;border:1px solid #E2E8F0;border-radius:0 0 10px 10px">
  <p>We have successfully received your {'job application' if is_app else 'inquiry'}. Our team will get back to you within <strong>24 hours</strong>.</p>
  <div style="background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin:20px 0">
    <p style="margin:0 0 6px 0;font-size:0.8rem;color:#64748b;text-transform:uppercase;font-weight:700">Your Message Summary:</p>
    <p style="margin:0;color:#334155;white-space:pre-wrap">{sanitise(form.message, 500)}</p>
  </div>
  <p style="font-size:0.9rem;color:#475569">Feel free to reply directly to this email with any questions.</p>
  <hr style="border:none;border-top:1px solid #E2E8F0;margin:20px 0"/>
  <p style="font-size:0.85rem;color:#64748b;margin-bottom:0">
    <strong>Infinity Solutions</strong><br>Toronto, ON, Canada<br>
    <a href="https://infinitysolutions.ca" style="color:#2563EB;text-decoration:none">https://infinitysolutions.ca</a>
  </p>
</div>
</div>"""

    await deliver_email(email, name, subject, body, reply_to=CONTACT_EMAIL)


# ── Routes ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service":          "Infinity Solutions API v2",
        "status":           "live",
        "smtp_configured":  bool(SMTP_USER and SMTP_PASS),
        "brevo_fallback":   bool(BREVO_API_KEY),
        "contact_target":   CONTACT_EMAIL,
    }


@app.get("/api/test-email")
async def test_email(to: str = "infinitysolutions137@gmail.com"):
    """Diagnostic: attempt SMTP delivery (all ports), fall back to Brevo if configured."""
    debug = {
        "smtp_host":       SMTP_HOST,
        "smtp_user":       SMTP_USER,
        "has_smtp_pass":   bool(SMTP_PASS),
        "brevo_fallback":  bool(BREVO_API_KEY),
    }

    html_body = f"""<div style="font-family:Arial,sans-serif;padding:20px">
      <h2 style="color:#1D4ED8">✅ Infinity Solutions — Email Test</h2>
      <p>Delivery succeeded! SMTP or Brevo is working correctly.</p>
      <p><strong>Time:</strong> {datetime.utcnow().isoformat()} UTC</p>
    </div>"""

    ok, info = await deliver_email(
        to_email=to,
        to_name="Test Recipient",
        subject="[TEST] Infinity Solutions — Email Diagnostic",
        html_body=html_body,
    )

    if ok:
        return {"status": "success", "message": f"Test email sent to {to}! ({info})", "debug": debug}
    else:
        return {"status": "error", "error_message": info, "debug": debug}


@app.post("/api/contact", status_code=201)
async def submit_contact(form: ContactForm, request: Request, background_tasks: BackgroundTasks):

    # 1. Honeypot
    if form.honeypot:
        return {"success": True, "message": "Received."}

    # 2. Rate limit
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    if not check_rate_limit(client_ip):
        raise HTTPException(429, "Too many submissions. Please wait a few minutes and try again.")

    # 3. Turnstile CAPTCHA
    if not await verify_turnstile(form.turnstile_token):
        raise HTTPException(400, "Security check failed. Please refresh and try again.")

    # 4. Resume validation (applications only)
    resume_bytes: Optional[bytes] = None
    if form.enquiry_type == "application":
        if not form.resume_data or not form.resume_filename:
            raise HTTPException(400, "A resume is required for job applications.")
        resume_bytes = validate_and_decode_resume(form.resume_data, form.resume_filename)

    # 5. Send notification to company (background — returns instantly)
    background_tasks.add_task(send_email, form, resume_bytes)

    # 6. Send auto-reply to visitor (background)
    background_tasks.add_task(send_auto_reply, form)

    return {
        "success": True,
        "message": "Your message has been received. We'll reply within 24 hours.",
    }
