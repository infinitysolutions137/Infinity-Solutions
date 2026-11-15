# Infinity Staffing v2 — AI-Powered Site

## What's New
- ✦ AI Chatbot (Aria) on every page — powered by Claude API
- ✦ Contact form emails account@infinitysolutions.ca (no public phone/email shown)
- ✦ Cloudflare Turnstile CAPTCHA on contact form (free, no puzzles)
- ✦ Hero with stunning background image + dark overlay
- ✦ Professional Asian/white imagery throughout
- ✦ Job share buttons: WhatsApp, LinkedIn, Facebook, Copy Link

## Files
```
infinity-v2/
├── index.html          — Home (hero + chatbot)
├── jobs-ai.html        — Jobs with AI match + share buttons
├── services-ai.html    — Services (IT, AI, Finance, Data)
├── about-ai.html       — About with AI process
├── contact-ai.html     — Contact (Turnstile CAPTCHA, no public info)
├── css/
│   ├── style.css       — Design system (CSS vars, components)
│   └── chatbot.css     — Aria chatbot widget styles
├── js/
│   ├── main.js         — Navbar, animations, tabs
│   ├── jobs.js         — Job data + filtering + share
│   └── chatbot.js      — Aria AI chatbot (Claude API)
└── backend/
    ├── main.py         — FastAPI: /api/contact → email
    └── requirements.txt
```

## Setup

### Frontend (static — just open index.html)
```bash
# Open directly OR use Live Server in VS Code
# OR:
python -m http.server 3000
```

### Backend (to enable real email sending)
```bash
cd backend
pip install -r requirements.txt

# Set environment variables:
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-gmail@gmail.com
export SMTP_PASS=your-app-password     # Gmail App Password
export TURNSTILE_SECRET=your-secret    # From dash.cloudflare.com

uvicorn main:app --reload --port 8000
```

## Cloudflare Turnstile Setup (free)
1. Go to https://dash.cloudflare.com → Turnstile
2. Add your site → get Sitekey + Secret Key
3. Replace `data-sitekey="0x4AAAAAAA"` in contact-ai.html with your sitekey
4. Set `TURNSTILE_SECRET` env var in backend

## Chatbot (Aria)
Aria uses the Claude API directly from the browser.
The `BOT_SYSTEM` prompt in js/chatbot.js defines her persona and rules.
She never shares phone/email — always redirects to the contact form.

## React Conversion Guide
Each HTML section maps directly to a React component:
- `<nav>` → `<Navbar />`
- `.job-card` → `<JobCard job={job} />`
- `.share-popover` → `<SharePopover job={job} />`
- `.chat-window` → `<ChatWidget />`
- `.filter-pill` → `<FilterPill />`
- `contactForm` → `<ContactForm />`
CSS variables map 1:1 to Tailwind config extension.
