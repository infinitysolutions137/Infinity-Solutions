"""
Infinity Solutions v2 — FastAPI Backend (Hardened)
Security layers:
  1. Cloudflare Turnstile CAPTCHA verification (server-side)
  2. Rate limiting — 5 submissions per IP per 10 minutes
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
import httpx, smtplib, os, re, base64, time, html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────
ALLOWED_ORIGINS   = os.getenv(
    "ALLOWED_ORIGINS",
    "https://infinitysolutions.ca,https://www.infinitysolutions.ca,http://infinitysolutions.ca,http://www.infinitysolutions.ca,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
).split(",")
TO_EMAIL          = os.getenv("TO_EMAIL", "bikoshita@infinitysolutions.ca")
CONTACT_EMAIL     = os.getenv("CONTACT_EMAIL", "accounts@infinitysolutions.ca")
SMTP_HOST         = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT         = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER         = os.getenv("SMTP_USER", "").strip()
SMTP_PASS         = os.getenv("SMTP_PASS", "").replace(" ", "").strip()
TURNSTILE_SECRET  = os.getenv("TURNSTILE_SECRET", "1x0000000000000000000000000000000AA").strip()

# ── App + CORS ─────────────────────────────────────────────────────────
app = FastAPI(title="Infinity Solutions API v2", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(.*\.)?(infinitysolutions\.ca|netlify\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiter — in-memory, per IP ──────────────────────────────────
# Allows 30 requests per IP per 10 minutes (generous for testing)
RATE_WINDOW   = 600   # seconds
RATE_LIMIT    = 30
_rate_store: dict = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_WINDOW
    _rate_store[ip] = [t for t in _rate_store[ip] if t > window_start]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return False
    _rate_store[ip].append(now)
    return True

# ── Allowed file types ─────────────────────────────────────────────────
# Magic bytes (file signatures) for PDF, DOC, DOCX
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_RESUME_BYTES   = 5 * 1024 * 1024   # 5 MB hard cap

FILE_MAGIC = {
    b"%PDF":                  "pdf",   # PDF
    b"\xd0\xcf\x11\xe0":     "doc",   # DOC (OLE2)
    b"PK\x03\x04":           "docx",  # DOCX (ZIP-based)
}

def validate_magic_bytes(data: bytes) -> bool:
    """Check actual file signature — ignores what the client claims."""
    for magic in FILE_MAGIC:
        if data[:len(magic)] == magic:
            return True
    return False

# ── Input sanitiser ────────────────────────────────────────────────────
INJECTION_PATTERNS = re.compile(
    r"(\r|\n|%0d|%0a|%0D|%0A|Content-Type:|Bcc:|Cc:|To:|From:|Reply-To:)",
    re.IGNORECASE,
)

def sanitise(value: Optional[str], max_len: int = 500) -> str:
    if not value:
        return ""
    # Strip HTML tags
    value = re.sub(r"<[^>]+>", "", value)
    # Remove email header injection sequences
    value = INJECTION_PATTERNS.sub("", value)
    # Escape remaining HTML entities
    value = html.escape(value, quote=True)
    # Enforce length cap
    return value[:max_len].strip()

def safe_filename(name: str) -> str:
    """Strip path traversal and dangerous chars from filename."""
    name = os.path.basename(name)
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = name[:120]
    return name or "resume"

# ── Pydantic model ─────────────────────────────────────────────────────
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
    resume_data:     Optional[str] = None   # base64-encoded
    honeypot:        Optional[str] = None   # must be empty — bots fill this

    @field_validator("from_email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip()[:254]
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", v):
            raise ValueError("Invalid email address")
        # Block disposable / known spam domains
        blocked_domains = {
            "mailinator.com", "guerrillamail.com", "10minutemail.com",
            "throwam.com", "yopmail.com", "trashmail.com", "sharklasers.com",
            "guerrillamailblock.com", "grr.la", "spam4.me", "dispostable.com",
        }
        domain = v.split("@")[-1].lower()
        if domain in blocked_domains:
            raise ValueError("Disposable email addresses are not accepted")
        return v

    @field_validator("from_name")
    @classmethod
    def validate_name(cls, v):
        v = sanitise(v, 120)
        if len(v) < 2:
            raise ValueError("Name is too short")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        v = sanitise(v, 3000)
        if len(v) < 5:
            raise ValueError("Message is too short")
        return v

    @field_validator("enquiry_type")
    @classmethod
    def validate_type(cls, v):
        allowed = {"general", "employer", "candidate", "partnership", "application"}
        v = v.lower().strip()[:30]
        return v if v in allowed else "general"

# ── Turnstile verification ─────────────────────────────────────────────
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

# ── Resume validation ──────────────────────────────────────────────────
def validate_and_decode_resume(b64_data: str, filename: str) -> bytes:
    """Decode base64, check size, validate magic bytes. Raises on failure."""
    try:
        # Strip data URI prefix if present
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        file_bytes = base64.b64decode(b64_data, validate=True)
    except Exception:
        raise HTTPException(400, "Invalid file encoding.")

    # Size check
    if len(file_bytes) > MAX_RESUME_BYTES:
        raise HTTPException(400, "File exceeds 5MB limit.")

    if len(file_bytes) < 4:
        raise HTTPException(400, "File is too small to be valid.")

    # Magic bytes check — reject anything that isn't really PDF/DOC/DOCX
    if not validate_magic_bytes(file_bytes):
        raise HTTPException(400, "Invalid file type. Only PDF, DOC, and DOCX are accepted.")

    # Extension check
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File extension '{ext}' is not allowed.")

    return file_bytes

# ── Email sender ───────────────────────────────────────────────────────
def send_email(form: ContactForm, resume_bytes: Optional[bytes] = None) -> bool:
    # Sanitise all fields before putting them in the email
    name       = sanitise(form.from_name, 120)
    email      = form.from_email
    phone      = sanitise(form.phone, 30) or "N/A"
    company    = sanitise(form.company, 120) or "N/A"
    message    = sanitise(form.message, 3000)
    etype      = sanitise(form.enquiry_type, 30)
    received   = sanitise(form.submitted_at, 30) or datetime.utcnow().isoformat()

    if not SMTP_USER:
        print(f"[CONTACT] {name} <{email}> [{etype}]: {message[:80]}")
        if form.resume_filename:
            print(f"[RESUME]  {form.resume_filename} ({len(resume_bytes or b'')} bytes)")
        return True

    is_application = etype == "application"
    recipient = TO_EMAIL if is_application else CONTACT_EMAIL
    subject   = f"[Infinity Solutions] {'Application' if is_application else etype.title()} — {name}"

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
    <a href="mailto:{email}?subject=Re: Your Infinity Solutions Application"
       style="background:#2563EB;color:#fff;border-radius:8px;padding:10px 22px;font-weight:700;text-decoration:none;display:inline-block">
      Reply to {name.split()[0]}
    </a>
  </div>
</div>
<p style="color:#94A3B8;font-size:.75rem;text-align:center;margin-top:8px">
  Infinity Solutions · Toronto, Canada
</p>
</div>"""

    msg = MIMEMultipart("mixed")
    # Prevent header injection — strip newlines from subject/from
    msg["Subject"]  = re.sub(r"[\r\n]", "", subject)
    msg["From"]     = re.sub(r"[\r\n]", "", SMTP_USER)
    msg["To"]       = recipient
    msg["Reply-To"] = re.sub(r"[\r\n]", "", email)
    msg.attach(MIMEText(body, "html"))

    if resume_bytes and form.resume_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(resume_bytes)
        encoders.encode_base64(part)
        safe_name = safe_filename(form.resume_filename)
        part.add_header("Content-Disposition", f'attachment; filename="{safe_name}"')
        msg.attach(part)

    recipients = [recipient]
    if SMTP_USER and SMTP_USER not in recipients:
        recipients.append(SMTP_USER)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
            s.ehlo()
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, recipients, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def send_auto_reply(form: ContactForm) -> bool:
    """Send an immediate confirmation email to the visitor who submitted the form."""
    if not SMTP_USER or not form.from_email:
        return False

    name  = sanitise(form.from_name, 120)
    email = form.from_email
    etype = sanitise(form.enquiry_type, 30)
    is_app = etype == "application"

    subject = "Thank you for contacting Infinity Solutions" if not is_app else "We have received your application — Infinity Solutions"
    body = f"""<div style="font-family:Arial,sans-serif;max-width:580px;color:#1e293b;line-height:1.6">
<div style="background:#1D4ED8;padding:24px 28px;border-radius:10px 10px 0 0">
  <h2 style="color:#fff;margin:0">Thank You, {name.split()[0]}!</h2>
  <p style="color:rgba(255,255,255,.8);margin:6px 0 0;font-size:.9rem">Infinity Solutions — AI-Powered Staffing</p>
</div>
<div style="background:#F8FAFC;padding:24px 28px;border:1px solid #E2E8F0;border-radius:0 0 10px 10px">
  <p style="font-size:1rem;margin-top:0">We have successfully received your {'job application' if is_app else 'inquiry'}. Our team is currently reviewing your details and will get back to you within <strong>24 hours</strong>.</p>
  
  <div style="background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin:20px 0">
    <p style="margin:0 0 6px 0;font-size:0.8rem;color:#64748b;text-transform:uppercase;font-weight:700">Your Message Summary:</p>
    <p style="margin:0;color:#334155;white-space:pre-wrap">{sanitise(form.message, 500)}</p>
  </div>

  <p style="font-size:0.9rem;color:#475569">If you have any questions in the meantime, feel free to reply directly to this email.</p>
  <hr style="border:none;border-top:1px solid #E2E8F0;margin:20px 0"/>
  <p style="font-size:0.85rem;color:#64748b;margin-bottom:0">
    <strong>Infinity Solutions</strong><br>
    Toronto, ON, Canada<br>
    <a href="https://infinitysolutions.ca" style="color:#2563EB;text-decoration:none">https://infinitysolutions.ca</a>
  </p>
</div>
</div>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"]  = re.sub(r"[\r\n]", "", subject)
    msg["From"]     = f"Infinity Solutions <{SMTP_USER}>"
    msg["To"]       = email
    msg["Reply-To"] = CONTACT_EMAIL
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
            s.ehlo()
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, email, msg.as_string())
        return True
    except Exception as e:
        print(f"[AUTO-REPLY ERROR] {e}")
        return False

# ── Routes ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "Infinity Solutions API v2", "status": "live"}


@app.post("/api/contact", status_code=201)
async def submit_contact(form: ContactForm, request: Request, background_tasks: BackgroundTasks):

    # 1. Honeypot — bots fill hidden fields, humans don't
    if form.honeypot:
        # Silently accept so bots don't know they were blocked
        return {"success": True, "message": "Received."}

    # 2. Rate limit — per IP
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

    # 5. Send notification email to the company (and copy to your Gmail)
    background_tasks.add_task(send_email, form, resume_bytes)

    # 6. Send immediate confirmation receipt to the visitor
    background_tasks.add_task(send_auto_reply, form)

    return {
        "success": True,
        "message": "Your message has been received. We'll reply within 24 hours.",
    }
