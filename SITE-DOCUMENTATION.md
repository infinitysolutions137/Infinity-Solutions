# Infinity Staffing Solutions — Full Site Documentation

**Version:** 7.0  
**Last updated:** June 2025  
**Owner:** Roy (Arindam Roy Chowdhury)  
**Live site:** infinitysolutions.ca

---

## Table of Contents

1. [Site Overview](#1-site-overview)
2. [File Structure](#2-file-structure)
3. [Do You Need a Database?](#3-do-you-need-a-database)
4. [How to Add Jobs Manually](#4-how-to-add-jobs-manually)
5. [How to Feature Jobs on the Services Page](#5-how-to-feature-jobs-on-the-services-page)
6. [How to Connect Ceipal](#6-how-to-connect-ceipal)
7. [How to Set Up the Contact Form Email](#7-how-to-set-up-the-contact-form-email)
8. [How to Set Up Cloudflare Turnstile CAPTCHA](#8-how-to-set-up-cloudflare-turnstile-captcha)
9. [How to Deploy the Site](#9-how-to-deploy-the-site)
10. [How to Deploy the Backend (Email API)](#10-how-to-deploy-the-backend-email-api)
11. [Future Upgrades Roadmap](#11-future-upgrades-roadmap)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Site Overview

The site is a **static HTML website** — no WordPress, no CMS, no complex server needed.

| Page | File | Purpose |
|---|---|---|
| Home | `index.html` | Hero, sector overview, AI features |
| Jobs | `jobs.html` | Ceipal live feed + curated job listings |
| Services | `services-ai.html` | Accordion by sector, featured job cards |
| About | `about-ai.html` | Team, process, values |
| Contact | `contact-ai.html` | Contact form → `accounts@infinitysolutions.ca` |

**Email routing:**
- Contact form → `accounts@infinitysolutions.ca`
- All job applications (Jobs page + Services page) → `bikoshita@infinitysolutions.ca`

**AI Chatbot:** Aria — powered by Claude API, floats on every page, knows all 6 sectors.

---

## 2. File Structure

```
infinity-v2/
│
├── index.html                  Home page
├── jobs.html                   Jobs page (Ceipal + curated)
├── services-ai.html            Services accordion
├── about-ai.html               About page
├── contact-ai.html             Contact form
│
├── css/
│   ├── style.css               Design system (colors, fonts, components)
│   └── chatbot.css             Aria chatbot widget styles
│
├── js/
│   ├── jobs.js                 ← ALL JOB DATA LIVES HERE
│   ├── chatbot.js              Aria AI chatbot logic (Claude API)
│   └── main.js                 Navbar, animations, scroll
│
├── backend/
│   ├── main.py                 FastAPI server — handles form email + CAPTCHA
│   └── requirements.txt        Python dependencies
│
├── HOW-TO-ADD-JOBS.md          Quick reference for adding jobs
├── SITE-DOCUMENTATION.md       This file
└── README.md                   Developer setup guide
```

---

## 3. Do You Need a Database?

### Short answer: No — not right now.

The site runs entirely without a database. Here is exactly what is stored where:

| Data | Where it lives | How to update |
|---|---|---|
| Job listings | `js/jobs.js` (plain text file) | Edit the file in VS Code |
| Contact form submissions | Email inbox (`accounts@infinitysolutions.ca`) | Check your email |
| Job applications | Email inbox (`bikoshita@infinitysolutions.ca`) | Check your email |
| Live jobs from Ceipal | Ceipal ATS (their cloud) | Manage in Ceipal dashboard |
| Site content | HTML files | Edit in VS Code |

### When would you need a database?

You would need a database when you want any of the following:

| Feature | Needs database? | Complexity |
|---|---|---|
| Add/edit jobs without touching code | ✅ Yes | Medium |
| Admin dashboard to manage jobs | ✅ Yes | Medium |
| Candidate profiles / accounts | ✅ Yes | High |
| Application tracking (who applied to what) | ✅ Yes | Medium |
| Employer portal | ✅ Yes | High |
| Email notifications when someone applies | ❌ No | Already works via SMTP |
| Ceipal integration | ❌ No | Ceipal handles it |
| Contact form | ❌ No | Already works |
| Blog / news section | ❌ No | Can be static HTML |

### Recommendation

**Stage 1 (now):** Static site + Ceipal ATS. Zero database needed. Ceipal handles all job management, applications, and candidate tracking on their platform. Your site just embeds their job board.

**Stage 2 (6–12 months):** If you want to manage jobs yourself without Ceipal, add a simple backend with a database. Good options:
- **Supabase** — free Postgres database, comes with an admin UI, very easy
- **Airtable** — spreadsheet-style database, no code needed, has an API
- **Firebase** — Google's free database, good for real-time updates

**Stage 3 (12+ months):** Full employer and candidate portal — React frontend + Node.js or Python backend + PostgreSQL database.

---

## 4. How to Add Jobs Manually

Jobs live in one file: **`js/jobs.js`**

Open it in VS Code (or any text editor). The file contains a `JOBS` array. Each job is one object inside that array.

### Step 1 — Find where to paste

Scroll to the bottom of `js/jobs.js`. Find the closing `];` at the very end. Paste your new job **before** that `];`.

### Step 2 — Copy this template

```javascript
{
  id:          'j019',                         // increment each time: j019, j020, j021...
  title:       'YOUR JOB TITLE',
  company:     'CLIENT COMPANY NAME',
  companyLogo: '💼',                           // one emoji — see table below
  location:    'Toronto, ON',
  remote:      false,                          // true = remote ok, false = on-site only
  sector:      'Technology',                   // exact string — see Sectors table below
  type:        'Permanent',                    // 'Permanent' or 'Contract'
  salary:      '$90k – $120k',
  salaryMin:   90000,                          // the lower number — used for sort
  posted:      '2025-06-10',                   // today's date in YYYY-MM-DD format
  match:       85,                             // AI match % shown on card — use 75 to 97
  tags:        ['Skill 1', 'Skill 2', 'Skill 3'],   // 3 to 5 skills
  desc:        'One or two sentence description of what the person will do.',
  hot:         false,                          // true shows a 🔥 Hot Role badge
},
```

### Sector strings — copy exactly

| Sector | String to use in the file |
|---|---|
| IT & Technology | `'Technology'` |
| Artificial Intelligence | `'Artificial Intelligence'` |
| Data & Analytics | `'Data & Analytics'` |
| Engineering | `'Engineering'` |
| Legal & Compliance | `'Legal & Compliance'` |
| Finance & Accounting | `'Finance & Accounting'` |

> ⚠️ Capitalisation matters. `'technology'` will not match — must be `'Technology'`.

### Emoji suggestions by sector

| Sector | Good choices |
|---|---|
| Technology | `💻` `🖥️` `☁️` `🔐` `⚙️` `📱` |
| AI | `🧠` `🤖` `🔬` `🚀` |
| Data | `📊` `📉` `🏗️` |
| Engineering | `⚙️` `⚡` `🏗️` `🏭` `🚗` |
| Legal | `⚖️` `🏛️` `🛡️` `👔` `📝` |
| Finance | `💰` `📈` `📋` `🏦` |

### Step 3 — Save and refresh

Save `js/jobs.js`. Refresh `jobs.html` in your browser. The new job appears automatically in the right sector filter.

### Checklist before saving

- [ ] `id` is unique and incremented (j019, j020…)
- [ ] `sector` string matches the table exactly
- [ ] `type` is `'Permanent'` or `'Contract'` (capital first letter)
- [ ] `remote` is `true` or `false` — no quotes around it
- [ ] `salaryMin` is a number — no quotes, no `$`, no `k`
- [ ] Comma after the closing `}` of your job object

### Full working example

```javascript
{
  id:          'j019',
  title:       'Immigration Lawyer',
  company:     'Maple Legal Group',
  companyLogo: '⚖️',
  location:    'Toronto, ON',
  remote:      true,
  sector:      'Legal & Compliance',
  type:        'Permanent',
  salary:      '$95k – $130k',
  salaryMin:   95000,
  posted:      '2025-06-10',
  match:       86,
  tags:        ['Immigration Law', 'IRCC', 'LSO Certified', 'French Asset'],
  desc:        'Advise corporate clients on Canadian immigration — work permits, LMIA, and permanent residency pathways.',
  hot:         false,
},
```

---

## 5. How to Feature Jobs on the Services Page

The Services page (`services-ai.html`) shows hand-picked jobs inside each accordion section. These are separate from `jobs.js` — they are written directly in the HTML.

### To add a job card to a section

1. Open `services-ai.html` in VS Code
2. Use Ctrl+F to search for the section (e.g. `acc-engineering`)
3. Find the `<div class="acc-jobs-grid">` inside that section
4. Copy one of the existing `<div class="mini-job">` blocks
5. Update these four values:
   - `mj-title` — job title
   - `mj-company` — company name and city
   - `mj-match-pct` — AI match % (keep it between 80 and 97)
   - `mj-meta` spans — location, salary, add `<span class="remote">⚡ Remote</span>` if remote
   - `mj-type` — Permanent or Contract
   - `onclick="openApply('Job Title', 'Company Name')"` — update both values

### Sector accent colours for the top bar

| Sector | Colour code |
|---|---|
| IT & Technology | `#3B82F6` |
| Artificial Intelligence | `#8B5CF6` |
| Data & Analytics | `#7C3AED` |
| Engineering | `#F97316` |
| Legal & Compliance | `#A855F7` |
| Finance & Accounting | `#10B981` |

---

## 6. How to Connect Ceipal

Ceipal provides an embed code (an iframe or script tag) that you paste into `jobs.html`. Once connected, all jobs you post in Ceipal appear on your site automatically.

### Steps

**In Ceipal:**
1. Log in to your Ceipal ATS account
2. Go to **Settings → Career Portal**
3. Look for **"Embed on your website"** or **"Get embed code"**
4. Copy the code they give you — it looks like one of these:

```html
<!-- Option A — iframe -->
<iframe
  src="https://app.ceipal.com/jobboard/YOUR-COMPANY-ID/jobs"
  width="100%"
  height="700"
  frameborder="0">
</iframe>

<!-- Option B — script -->
<div id="ceipal-job-board"></div>
<script src="https://app.ceipal.com/embed/YOUR-COMPANY-ID.js"></script>
```

**In your site files:**
1. Open `jobs.html` in VS Code
2. Find this comment (use Ctrl+F):
   ```
   <!-- YOUR CEIPAL IFRAME OR SCRIPT GOES HERE -->
   ```
3. Paste your Ceipal code on that line
4. Scroll up slightly and **delete** the entire `<div class="ceipal-placeholder">` block (it starts with `<!-- PLACEHOLDER` and ends with `<!-- END PLACEHOLDER -->`)
5. Save `jobs.html`
6. Upload/deploy — done. Your Ceipal jobs now appear live

### If the Ceipal iframe is cut off

Find this CSS in `jobs.html`:
```css
.ceipal-live-embed {
  min-height: 700px;
}
```
Increase `700px` to `900px` or `1100px` until all jobs are visible.

---

## 7. How to Set Up the Contact Form Email

The contact form sends to `accounts@infinitysolutions.ca` via the FastAPI backend.

### Requirements

You need a Gmail account (or any SMTP provider) to act as the sender.

### Gmail setup

1. Log into Gmail → Account → Security → **2-Step Verification** (turn on if not already)
2. Go to **App Passwords** (search in Google account settings)
3. Create a new App Password — call it "Infinity Staffing Site"
4. Copy the 16-character password Google gives you

### Running the backend

```bash
cd backend

# Install dependencies (once)
pip install -r requirements.txt

# Set environment variables
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-gmail@gmail.com       # the sender Gmail address
export SMTP_PASS=xxxx xxxx xxxx xxxx        # the App Password from step 4
export TURNSTILE_SECRET=your-secret-key     # from Cloudflare (see section 8)

# Start the server
uvicorn main:app --reload --port 8000
```

The backend runs at `http://localhost:8000`. When deployed, your site's form will POST to `/api/contact` on whatever server you host it on.

### To change where contact form emails go

Open `backend/main.py`, find this line and update it:
```python
TO_EMAIL = "accounts@infinitysolutions.ca"
```

### To change where applications go

Same file, the form payload sets `to: 'bikoshita@infinitysolutions.ca'` — this is set in the JavaScript inside `jobs.html` and `services-ai.html`. Search for `bikoshita@infinitysolutions.ca` to find all instances.

---

## 8. How to Set Up Cloudflare Turnstile CAPTCHA

Turnstile is a free, invisible CAPTCHA from Cloudflare — no image puzzles, no monthly limits.

### Get your keys (free, 5 minutes)

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) — create a free account if needed
2. In the left sidebar click **Turnstile**
3. Click **Add site**
4. Enter your domain (`infinitysolutions.ca`), choose **Managed** mode
5. Click Create — Cloudflare gives you two keys:
   - **Site Key** — goes in your HTML (public, safe to share)
   - **Secret Key** — goes in your backend environment variable (keep private)

### Add your Site Key to the contact form

Open `contact-ai.html`. Find this line:
```html
data-sitekey="0x4AAAAAAA"
```
Replace `0x4AAAAAAA` with your real Site Key.

### Add your Secret Key to the backend

```bash
export TURNSTILE_SECRET=your-real-secret-key-here
```

That's it. The CAPTCHA will now verify real users and block bots.

---

## 9. How to Deploy the Site

The HTML files are static — they can be hosted anywhere for free.

### Option A — Netlify (recommended, free)

1. Go to [netlify.com](https://netlify.com) and sign up free
2. Drag and drop your `infinity-v2` folder onto the Netlify dashboard
3. Your site goes live instantly at a random URL (e.g. `random-name.netlify.app`)
4. Go to **Domain settings** → add `infinitysolutions.ca`
5. Point your domain's DNS to Netlify (they show you exactly what to change)
6. Free SSL certificate applied automatically

**For the backend (email API):** Deploy separately — see section 10.

### Option B — GitHub Pages (free, good for static)

1. Create a GitHub account and a new repository called `infinity-staffing-site`
2. Upload all files in `infinity-v2/` to the repository
3. Go to repo **Settings → Pages → Source → main branch**
4. Site goes live at `yourusername.github.io/infinity-staffing-site`
5. Add your custom domain in the Pages settings

> Note: GitHub Pages cannot run the Python backend. You need a separate server for email sending (Render, Railway, or Heroku — all have free tiers).

### Option C — Your own server / VPS

If you already have web hosting (cPanel, DirectAdmin, etc.):
1. Upload all files in `infinity-v2/` to the `public_html` folder via FTP
2. Done — site is live

---

## 10. How to Deploy the Backend (Email API)

The backend (`backend/main.py`) is a Python FastAPI server. It needs to run somewhere permanently for the contact form to send emails.

### Option A — Render (free tier available)

1. Go to [render.com](https://render.com) — sign up free
2. New → **Web Service** → connect your GitHub repo
3. Set **Root Directory** to `backend`
4. Set **Build Command** to `pip install -r requirements.txt`
5. Set **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables in the Render dashboard:
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = your Gmail
   - `SMTP_PASS` = your App Password
   - `TURNSTILE_SECRET` = your Cloudflare secret key
7. Deploy — Render gives you a URL like `https://infinity-api.onrender.com`
8. In `contact-ai.html`, update the fetch URL from `/api/contact` to `https://infinity-api.onrender.com/api/contact`

### Option B — Railway (simple, ~$5/month)

Similar to Render but more reliable uptime. Go to [railway.app](https://railway.app), connect GitHub, set the same environment variables.

### Option C — Skip the backend entirely (EmailJS)

If you don't want to run a Python server at all, use [EmailJS](https://emailjs.com) — it lets you send email directly from the browser JavaScript. Free up to 200 emails/month.

1. Sign up at emailjs.com
2. Connect your Gmail
3. Replace the `fetch('/api/contact', ...)` call in `contact-ai.html` with EmailJS's 3-line snippet
4. No server needed

---

## 11. Future Upgrades Roadmap

### Near term (0–3 months) — no database needed

| Upgrade | Effort | How |
|---|---|---|
| Connect Ceipal embed | 30 minutes | Section 6 above |
| Real email sending | 1 hour | Sections 7–10 above |
| Turnstile CAPTCHA live | 30 minutes | Section 8 above |
| Google Analytics | 15 minutes | Paste GA4 tag in `<head>` of all pages |
| WhatsApp chat button | 30 minutes | Add `wa.me/` link button to pages |

### Medium term (3–6 months) — light backend, still no database

| Upgrade | Effort | Notes |
|---|---|---|
| Blog / news section | 2–4 hours | Static HTML pages, no CMS needed |
| Testimonials section | 2 hours | Add to `index.html` |
| Team profiles page | 2 hours | New static HTML page |
| SEO improvements | 4 hours | Add meta tags, sitemap.xml, robots.txt |
| LinkedIn job share tracking | 1 hour | Add UTM parameters to share links |

### Longer term (6–12 months) — needs a database

| Upgrade | What it unlocks | Recommended stack |
|---|---|---|
| Admin panel to manage jobs | Add/edit/delete jobs without touching code | Supabase (free) + simple React form |
| Candidate profiles | Candidates create accounts, save jobs, track applications | Supabase Auth + Postgres |
| Application tracking | See all applicants per role in a dashboard | Supabase + React table |
| Employer portal | Clients post jobs, review CVs, give feedback | Supabase + React, ~3 months work |
| AI matching engine | Real AI scoring instead of static numbers | Python ML model + Postgres |
| Automated email sequences | Follow-up emails to applicants automatically | SendGrid or Resend + database |

### Recommended database if/when you need one

**Supabase** — best choice for this site:
- Free tier: 500MB database, 2GB storage, 50,000 monthly active users
- Comes with a built-in admin UI (like a spreadsheet for your data)
- Has authentication built in (for candidate/employer logins)
- Works well with the existing Python/FastAPI backend
- No DevOps knowledge required

---

## 12. Troubleshooting

### Jobs not showing on the page

- Open `js/jobs.js` in VS Code
- Look for red underlines or error highlights — there may be a syntax error (missing comma, unclosed bracket)
- Open the browser Console (F12 → Console tab) — any JavaScript errors will show there
- Most common mistake: missing comma after the closing `}` of a job object

### Contact form says "Something went wrong"

- The backend server (`backend/main.py`) is not running — start it with `uvicorn main:app --reload --port 8000`
- Check that your SMTP environment variables are set correctly
- Gmail App Password must be the 16-character code, not your regular Gmail password

### Ceipal iframe not showing

- Make sure you deleted the `ceipal-placeholder` div after pasting the embed code
- If the iframe shows but jobs are cut off, increase `min-height` in the CSS (see section 6)
- Ceipal may require your domain to be whitelisted in their portal settings — check with Ceipal support

### Aria chatbot not responding

- The Claude API key is embedded in `js/chatbot.js` — check it hasn't expired
- Open browser Console (F12) and look for API errors
- The chatbot calls `https://api.anthropic.com/v1/messages` directly from the browser — make sure your API key has sufficient credits

### Site looks broken after editing HTML

- Most likely a missing `>` or `"` in the HTML you edited
- Use VS Code — it highlights HTML errors in red
- Press Ctrl+Z to undo recent changes if needed

### How to update a job that's already live

Open `js/jobs.js`, find the job by its `id` or `title`, edit the values, save the file, and re-upload to your hosting. The change appears immediately on refresh.

### How to remove a job

Open `js/jobs.js`, find the job object, delete the entire block from `{` to `},` (including the comma). Save and re-upload.

---

## Quick Reference Card

| Task | File to edit |
|---|---|
| Add a new job | `js/jobs.js` |
| Remove a job | `js/jobs.js` |
| Feature a job on Services page | `services-ai.html` |
| Connect Ceipal | `jobs.html` |
| Change contact form email | `backend/main.py` → `TO_EMAIL` |
| Change apply email | Search `bikoshita@infinitysolutions.ca` in HTML files |
| Update Turnstile sitekey | `contact-ai.html` → `data-sitekey` |
| Change Aria's personality | `js/chatbot.js` → `BOT_SYSTEM` constant |
| Add a page to the navbar | Edit `<ul class="nav-links">` in each HTML file |
| Change site colours | `css/style.css` → `:root` variables at the top |

