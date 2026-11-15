# How to Add Jobs Manually — Infinity Staffing Site

## Overview
Jobs live in one file: `js/jobs.js`
Open that file in VS Code (or any text editor) and follow the steps below.

---

## Step 1 — Open js/jobs.js

The file starts with `const JOBS = [` followed by a list of job objects.
Each job looks like this:

```js
{
  id:          'j019',                    // ← unique ID (increment each time)
  title:       'Senior React Developer',  // ← job title
  company:     'Acme Corp',               // ← client company name
  companyLogo: '💻',                      // ← one emoji representing the role
  location:    'Toronto, ON',             // ← city, province
  remote:      true,                      // ← true or false
  sector:      'Technology',              // ← see Sectors list below
  type:        'Permanent',               // ← 'Permanent' or 'Contract'
  salary:      '$110k – $135k',           // ← salary range (display string)
  salaryMin:   110000,                    // ← lowest number (used for sorting)
  posted:      '2025-06-01',              // ← date posted  YYYY-MM-DD
  match:       88,                        // ← AI match % shown on card (60–99)
  tags:        ['React', 'TypeScript', 'Node.js', 'AWS'],  // ← 3–5 skills
  desc:        'Build and scale the front-end of our AI SaaS platform.',
  hot:         false,                     // ← true shows a 🔥 Hot Role badge
},
```

---

## Step 2 — Copy the template and fill it in

Copy this block, paste it **before the closing `];`** at the bottom of the JOBS array,
and fill in your values:

```js
{
  id:          'j019',
  title:       'YOUR JOB TITLE HERE',
  company:     'COMPANY NAME',
  companyLogo: '💼',
  location:    'Toronto, ON',
  remote:      false,
  sector:      'Technology',
  type:        'Permanent',
  salary:      '$90k – $120k',
  salaryMin:   90000,
  posted:      '2025-06-01',
  match:       85,
  tags:        ['Skill 1', 'Skill 2', 'Skill 3'],
  desc:        'One or two sentence description of the role and what the person will do.',
  hot:         false,
},
```

> **Important:** increment the `id` each time (j019, j020, j021…)
> Make sure you have a comma after the closing `}` unless it's the very last item.

---

## Step 3 — Choose the right Sector

Use exactly one of these sector names (copy-paste to avoid typos):

| Sector string to use        | Shows under              |
|-----------------------------|--------------------------|
| `'Technology'`              | IT & Technology filter   |
| `'Artificial Intelligence'` | AI filter                |
| `'Data & Analytics'`        | Data filter              |
| `'Engineering'`             | Engineering filter       |
| `'Legal & Compliance'`      | Legal filter             |
| `'Finance & Accounting'`    | Finance filter           |

---

## Step 4 — Choose a matching emoji for companyLogo

| Sector              | Good emojis                        |
|---------------------|------------------------------------|
| Technology          | 💻 🖥️ ☁️ 🔐 ⚙️                    |
| Artificial Intelligence | 🧠 🤖 🔬 🚀                    |
| Data & Analytics    | 📊 📉 🏗️ 🔬                       |
| Engineering         | ⚙️ ⚡ 🏗️ 🏭 🔬 🚗                |
| Legal & Compliance  | ⚖️ 🏛️ 🛡️ 🔏 📝 👔               |
| Finance & Accounting| 💰 📈 📋 🏦 🔍                    |

---

## Step 5 — Save and refresh

Save `js/jobs.js` and refresh the browser.
The new job will appear automatically on:
- The **Jobs page** (`jobs-ai.html`) in the correct sector filter
- The **Services page** (`services-ai.html`) accordion "Featured Openings" section
  *(only the 2–4 manually featured jobs show there — see below)*

---

## How to feature a job on the Services page

The Services page (`services-ai.html`) shows hand-picked "Featured Openings"
inside each accordion section. These are written directly in the HTML —
they don't pull from `jobs.js` automatically.

To add a new one:

1. Open `services-ai.html`
2. Find the accordion section you want (search for `acc-tech`, `acc-engineering`, etc.)
3. Find the `<div class="acc-jobs-grid">` inside that section
4. Copy an existing `<div class="mini-job">` block and edit the values:
   - `mj-title` — job title
   - `mj-company` — company and city
   - `mj-match-pct` — AI match % (make it realistic: 80–97)
   - `mj-meta` spans — location, salary, Remote if applicable
   - `mj-type` — Permanent or Contract
   - `onclick="openApply('Job Title','Company Name')"` — update both

---

## Where applications go

Every "Apply Now" click on the site sends an email to:

```
bikoshita@infinitysolutions.ca
```

The email includes: applicant name, email, phone, LinkedIn, cover note, and the job they applied for.

To change the email address, update this line in `backend/main.py`:

```python
TO_EMAIL = "bikoshita@infinitysolutions.ca"
```

---

## Quick checklist when adding a new job

- [ ] Incremented the `id` (j019, j020…)
- [ ] Correct `sector` string (exact match from the table above)
- [ ] `type` is either `'Permanent'` or `'Contract'` (capital P/C)
- [ ] `remote` is `true` or `false` (no quotes)
- [ ] Comma after the closing `}` of the job object
- [ ] Saved the file and refreshed the browser

---

## Example — complete filled-in job

```js
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
  posted:      '2025-06-05',
  match:       86,
  tags:        ['Immigration Law', 'IRCC', 'LSO', 'French Asset'],
  desc:        'Advise corporate clients on Canadian immigration matters including work permits, LMIA applications, and permanent residency pathways.',
  hot:         false,
},
```
