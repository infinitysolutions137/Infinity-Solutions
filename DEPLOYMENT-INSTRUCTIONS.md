# Deployment Instructions — infinitysolutions.ca
## For the Developer

**Client:** Roy (Arindam Roy Chowdhury) — Infinity Solutions  
**Domain:** infinitysolutions.ca  
**Stack:** Static HTML/CSS/JS frontend + Python FastAPI backend  
**Zip file:** infinity-v15-captcha.zip

---

## What You're Deploying

| Part | What it is | Where it goes |
|---|---|---|
| HTML/CSS/JS files | The website (5 pages) | Any static host (Netlify recommended) |
| `backend/main.py` | Python API — handles email + CAPTCHA | Separate server (Render recommended) |

---

## Part 1 — Deploy the Website (Static Files)

### Recommended: Netlify (free)

1. Go to [netlify.com](https://netlify.com) and sign in / create account
2. From the dashboard click **"Add new site" → "Deploy manually"**
3. Unzip `infinity-v15-captcha.zip` — you'll get a folder called `infinity-v2`
4. Drag and drop the **`infinity-v2` folder** onto the Netlify deploy area
5. Site goes live immediately at a random URL like `random-name.netlify.app`
6. Go to **Site settings → Domain management → Add custom domain**
7. Type `infinitysolutions.ca` and follow Netlify's DNS instructions
8. Netlify will tell you to add two DNS records at your domain registrar — add them
9. Click **"Verify DNS configuration"** — SSL certificate applies automatically (free)
10. Site is live at `https://infinitysolutions.ca` ✓

> **Alternative hosts that also work:** Cloudflare Pages, GitHub Pages, Vercel, or any cPanel/FTP hosting. Just upload the contents of the `infinity-v2` folder to the `public_html` directory.

---

## Part 2 — Deploy the Backend (Email + CAPTCHA API)

The backend is needed for:
- Contact form sending email to `accounts@infinitysolutions.ca`
- Job applications sending email + resume to `bikoshita@infinitysolutions.ca`
- Server-side Cloudflare Turnstile CAPTCHA verification

### Recommended: Render (free tier available)

1. Create a GitHub account if not already done
2. Create a new **private** repository — e.g. `infinity-backend`
3. Upload only the `backend/` folder contents (`main.py` + `requirements.txt`) to that repo
4. Go to [render.com](https://render.com) → **New → Web Service**
5. Connect the GitHub repository
6. Set these build settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python version:** 3.11
7. Add the following **Environment Variables** in the Render dashboard:

| Variable | Value | Where to get it |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | Fixed value |
| `SMTP_PORT` | `587` | Fixed value |
| `SMTP_USER` | Roy's Gmail address | Roy to provide |
| `SMTP_PASS` | Gmail App Password (16 chars) | Roy to generate — see below |
| `TURNSTILE_SECRET` | Cloudflare secret key | Roy to provide — see below |
| `ALLOWED_ORIGINS` | `https://infinitysolutions.ca` | The live domain |

8. Click **Deploy** — Render gives a URL like `https://infinity-api.onrender.com`
9. Copy that URL

---

## Part 3 — Connect Frontend to Backend

Once the backend is deployed, update one line in the frontend:

1. Open `contact-ai.html`
2. Find this line (around line 310):
   ```javascript
   const res = await fetch('/api/contact', {
   ```
3. Change it to:
   ```javascript
   const res = await fetch('https://infinity-api.onrender.com/api/contact', {
   ```
4. Do the same in `jobs.html` — search for `/api/contact` (appears twice — job apply and profile upload)
5. Re-upload / redeploy the updated HTML files to Netlify

---

## Part 4 — Set Up Cloudflare Turnstile (Free CAPTCHA)

The contact form and all upload modals use Cloudflare Turnstile. Roy needs to set this up once.

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) — create free account if needed
2. In the sidebar click **Turnstile**
3. Click **Add site**
   - Name: `Infinity Solutions`
   - Domain: `infinitysolutions.ca`
   - Widget type: **Managed** (invisible, no puzzles for real users)
4. Click Create — you get two keys:
   - **Site Key** (public) — goes in the HTML
   - **Secret Key** (private) — goes in the backend env var

**Update the Site Key in HTML files:**

In `contact-ai.html` find:
```html
data-sitekey="0x4AAAAAAA"
```
Replace `0x4AAAAAAA` with the real Site Key.

In `jobs.html` find (appears once near the bottom):
```javascript
const TURNSTILE_SITEKEY = '0x4AAAAAAA';
```
Replace with the real Site Key.

In `services-ai.html` find:
```javascript
const TURNSTILE_SITEKEY = '0x4AAAAAAA';
```
Replace with the real Site Key.

**Set the Secret Key in Render:**
Add it as the `TURNSTILE_SECRET` environment variable (step 7 in Part 2).

---

## Part 5 — Set Up Gmail App Password (for email sending)

Roy needs to do this — it takes 3 minutes.

1. Log into the Gmail account that will send emails (e.g. `noreply@infinitysolutions.ca` or Roy's Gmail)
2. Go to **Google Account → Security**
3. Make sure **2-Step Verification is ON** (required)
4. Search for **"App Passwords"** in the Google Account settings
5. Click **Create** — name it "Infinity Solutions Site"
6. Google shows a **16-character password** — copy it immediately (shown once only)
7. Give this password to the developer to set as `SMTP_PASS` in Render

---

## Part 6 — Final Checks After Deployment

The developer should test each of these before handing over:

- [ ] `https://infinitysolutions.ca` loads correctly
- [ ] `https://infinitysolutions.ca/jobs.html` shows all job listings
- [ ] `https://infinitysolutions.ca/services-ai.html` accordion opens correctly
- [ ] Contact form on `contact-ai.html` — submit a test message, confirm email arrives at `accounts@infinitysolutions.ca`
- [ ] Apply Now on a job — upload a PDF resume, confirm email + attachment arrives at `bikoshita@infinitysolutions.ca`
- [ ] Upload Profile button — confirm it opens a modal (not redirect to contact page)
- [ ] Aria chatbot — click the blue chat button bottom-right, send a message, confirm it responds
- [ ] Turnstile CAPTCHA visible on contact form and apply modals
- [ ] SSL certificate active — padlock shows in browser (`https://`)
- [ ] Mobile view — test on a phone, confirm navbar and modals work

---

## Summary — What Roy Needs to Prepare

Before the developer starts, Roy should have these ready:

| Item | What it is | Where |
|---|---|---|
| Gmail App Password | 16-character code | Google Account → Security → App Passwords |
| Cloudflare Turnstile Site Key | Public key for HTML | dash.cloudflare.com → Turnstile |
| Cloudflare Turnstile Secret Key | Private key for backend | dash.cloudflare.com → Turnstile |
| Access to domain registrar | To update DNS records | Wherever `infinitysolutions.ca` is registered |

---

## Questions?

The full technical documentation is in `SITE-DOCUMENTATION.md` inside the zip.  
All files are in the `infinity-v2/` folder inside `infinity-v15-captcha.zip`.

**Contact Roy:** arindam@infinitysolutions.ca  
**Live domain:** https://infinitysolutions.ca
