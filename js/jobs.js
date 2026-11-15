/* ═══════════════════════════════════════════════════════════════════════════
   jobs.js — Job data + filtering engine
   React-ready: export JOBS and filterJobs() as named exports when converting
   ═══════════════════════════════════════════════════════════════════════════ */

'use strict';

/* ── Data ──────────────────────────────────────────────────────────────── */
const JOBS = [
  {
    id: 'j001', title: 'AI/ML Engineer', company: 'Nexus AI Labs', companyLogo: '🧠',
    location: 'Toronto, ON', remote: true, sector: 'Artificial Intelligence',
    type: 'Permanent', salary: '$130k – $165k', salaryMin: 130000, posted: '2026-08-05',
    match: 97, tags: ['Python', 'PyTorch', 'LLMs', 'MLOps'],
    desc: 'Lead the development of production-grade ML models and LLM-powered pipelines for enterprise AI products.', hot: true,
  },
  {
    id: 'j002', title: 'Senior Software Engineer', company: 'TechCorp Canada', companyLogo: '💻',
    location: 'Vancouver, BC', remote: true, sector: 'Technology',
    type: 'Permanent', salary: '$120k – $150k', salaryMin: 120000, posted: '2026-08-14',
    match: 94, tags: ['Python', 'AWS', 'Microservices', 'React'],
    desc: 'Build scalable backend systems powering AI-driven SaaS platforms serving 500k+ users across North America.', hot: false,
  },
  {
    id: 'j003', title: 'Data Scientist', company: 'AnalyticsX', companyLogo: '📊',
    location: 'Montreal, QC', remote: true, sector: 'Data & Analytics',
    type: 'Contract', salary: '$110k – $140k', salaryMin: 110000, posted: '2026-08-11',
    match: 91, tags: ['Python', 'TensorFlow', 'SQL', 'Tableau'],
    desc: 'Drive predictive analytics and AI model development for fintech clients — owning the full data science lifecycle.', hot: true,
  },
  {
    id: 'j004', title: 'Cloud Architect (AWS)', company: 'Global Dynamics', companyLogo: '☁️',
    location: 'Toronto, ON', remote: false, sector: 'Technology',
    type: 'Contract', salary: '$140k – $175k', salaryMin: 140000, posted: '2026-08-20',
    match: 89, tags: ['AWS', 'Terraform', 'Kubernetes', 'DevSecOps'],
    desc: 'Architect and govern enterprise cloud infrastructure supporting AI workloads at scale for Fortune 500 clients.', hot: false,
  },
  {
    id: 'j005', title: 'ERP Business Analyst', company: 'SysCore Inc.', companyLogo: '⚙️',
    location: 'Ottawa, ON', remote: true, sector: 'Technology',
    type: 'Contract', salary: '$95k – $120k', salaryMin: 95000, posted: '2026-08-17',
    match: 86, tags: ['SAP', 'S/4HANA', 'Business Analysis', 'SQL'],
    desc: 'Lead SAP S/4HANA implementation and process optimisation for large-scale enterprise digital transformation.', hot: false,
  },
  {
    id: 'j006', title: 'Product Manager — AI Products', company: 'Synaptic Labs', companyLogo: '🚀',
    location: 'Toronto, ON', remote: true, sector: 'Artificial Intelligence',
    type: 'Permanent', salary: '$125k – $155k', salaryMin: 125000, posted: '2026-08-08',
    match: 92, tags: ['AI Strategy', 'Roadmapping', 'Agile', 'LLMs'],
    desc: 'Own the product vision and roadmap for a suite of enterprise AI tools used by 200+ global companies.', hot: true,
  },
  {
    id: 'j007', title: 'Senior Financial Analyst', company: 'NorthStar Capital', companyLogo: '💰',
    location: 'Calgary, AB', remote: true, sector: 'Finance & Accounting',
    type: 'Permanent', salary: '$88k – $108k', salaryMin: 88000, posted: '2026-08-26',
    match: 83, tags: ['Financial Modelling', 'Excel', 'FP&A', 'M&A'],
    desc: 'Drive financial planning, M&A analysis, and strategic reporting for a high-growth investment portfolio.', hot: false,
  },
  {
    id: 'j008', title: 'Cybersecurity Engineer', company: 'ShieldNet Canada', companyLogo: '🔐',
    location: 'Toronto, ON', remote: false, sector: 'Technology',
    type: 'Permanent', salary: '$115k – $145k', salaryMin: 115000, posted: '2026-08-23',
    match: 88, tags: ['Zero Trust', 'SIEM', 'Penetration Testing', 'SOC2'],
    desc: 'Design and implement AI-assisted threat detection systems protecting critical cloud infrastructure.', hot: false,
  },
  {
    id: 'j009', title: 'Full-Stack Developer', company: 'BuildFast Digital', companyLogo: '🖥️',
    location: 'Winnipeg, MB', remote: true, sector: 'Technology',
    type: 'Contract', salary: '$95k – $120k', salaryMin: 95000, posted: '2026-08-29',
    match: 85, tags: ['React', 'Node.js', 'TypeScript', 'PostgreSQL'],
    desc: 'Build and scale AI-powered digital products from scratch — full ownership from API to pixel.', hot: false,
  },
  {
    id: 'j010', title: 'Corporate Controller', company: 'PrecisionBooks Ltd.', companyLogo: '📋',
    location: 'Mississauga, ON', remote: true, sector: 'Finance & Accounting',
    type: 'Permanent', salary: '$120k – $145k', salaryMin: 120000, posted: '2026-09-01',
    match: 80, tags: ['GAAP', 'CPA', 'Financial Reporting', 'ERP'],
    desc: 'Lead all financial operations, reporting, and compliance for a rapidly scaling SaaS company.', hot: false,
  },
  // ── ENGINEERING ───────────────────────────────────────────────
  {
    id: 'j011', title: 'Mechanical Engineer — Product Design', company: 'PrecisionTech Industries', companyLogo: '⚙️',
    location: 'Mississauga, ON', remote: false, sector: 'Engineering',
    type: 'Permanent', salary: '$90k – $115k', salaryMin: 90000, posted: '2026-08-02',
    match: 88, tags: ['SolidWorks', 'FEA', 'CATIA', 'P.Eng'],
    desc: 'Lead product design and mechanical systems development for advanced industrial and consumer hardware products.', hot: true,
  },
  {
    id: 'j012', title: 'Electrical Engineer — Power Systems', company: 'VoltCore Energy', companyLogo: '⚡',
    location: 'Calgary, AB', remote: false, sector: 'Engineering',
    type: 'Permanent', salary: '$95k – $125k', salaryMin: 95000, posted: '2026-08-08',
    match: 85, tags: ['PLC', 'SCADA', 'HV Systems', 'MATLAB'],
    desc: 'Design and commission high-voltage power systems and control infrastructure for energy sector clients.', hot: false,
  },
  {
    id: 'j013', title: 'Civil / Structural Engineer', company: 'BuildBridge Consultants', companyLogo: '🏗️',
    location: 'Vancouver, BC', remote: false, sector: 'Engineering',
    type: 'Contract', salary: '$100k – $130k', salaryMin: 100000, posted: '2026-08-17',
    match: 82, tags: ['Revit', 'AutoCAD', 'STAAD.Pro', 'P.Eng'],
    desc: 'Lead structural analysis and design for commercial and mixed-use developments in Greater Vancouver.', hot: false,
  },
  {
    id: 'j014', title: 'Automotive EV Engineer', company: 'NextDrive Motors', companyLogo: '🚗',
    location: 'Windsor, ON', remote: false, sector: 'Engineering',
    type: 'Permanent', salary: '$105k – $135k', salaryMin: 105000, posted: '2026-08-11',
    match: 90, tags: ['EV Powertrain', 'AUTOSAR', 'CAN Bus', 'HIL Testing'],
    desc: 'Design and validate next-generation EV powertrain systems — from battery management to motor control.', hot: true,
  },
  // ── LEGAL ─────────────────────────────────────────────────────
  {
    id: 'j015', title: 'In-House Counsel — Tech', company: 'Synaptic Labs', companyLogo: '🏛️',
    location: 'Toronto, ON', remote: true, sector: 'Legal & Compliance',
    type: 'Permanent', salary: '$130k – $165k', salaryMin: 130000, posted: '2026-07-30',
    match: 93, tags: ['Commercial Law', 'IP', 'SaaS Contracts', 'LSO'],
    desc: 'First in-house legal hire at a high-growth AI company — managing contracts, IP strategy, privacy, and regulatory matters.', hot: true,
  },
  {
    id: 'j016', title: 'Privacy & Data Protection Lawyer', company: 'ShieldNet Canada', companyLogo: '🔏',
    location: 'Toronto, ON', remote: true, sector: 'Legal & Compliance',
    type: 'Permanent', salary: '$120k – $155k', salaryMin: 120000, posted: '2026-08-05',
    match: 91, tags: ['PIPEDA', 'GDPR', 'Bill C-27', 'CIPP/C'],
    desc: "Lead privacy compliance for a cybersecurity firm — advising on PIPEDA, GDPR, and Canada's new Bill C-27 framework.", hot: true,
  },
  {
    id: 'j017', title: 'Compliance Officer — Financial Services', company: 'NorthStar Capital', companyLogo: '🛡️',
    location: 'Toronto, ON', remote: false, sector: 'Legal & Compliance',
    type: 'Permanent', salary: '$110k – $140k', salaryMin: 110000, posted: '2026-08-14',
    match: 87, tags: ['AML / KYC', 'OSFI', 'FINTRAC', 'Risk Management'],
    desc: 'Own AML/KYC compliance frameworks and regulatory reporting for a growing investment management firm.', hot: false,
  },
  {
    id: 'j018', title: 'Corporate / M&A Lawyer', company: 'Bay Street Partners LLP', companyLogo: '👔',
    location: 'Toronto, ON', remote: false, sector: 'Legal & Compliance',
    type: 'Permanent', salary: '$140k – $200k', salaryMin: 140000, posted: '2026-08-20',
    match: 89, tags: ['M&A', 'Securities Law', 'Due Diligence', 'LSO'],
    desc: 'Senior associate role at a top-tier Bay Street firm — leading M&A transactions and securities offerings for major corporations.', hot: false,
  },
];

/* ── Sector colors ─────────────────────────────────────────────────────── */
const SECTOR_STYLE = {
  'Artificial Intelligence': { bg: '#EFF6FF', border: '#BFDBFE', color: '#1D4ED8' },
  'Technology':              { bg: '#F0F9FF', border: '#BAE6FD', color: '#0369A1' },
  'Data & Analytics':        { bg: '#F5F3FF', border: '#DDD6FE', color: '#5B21B6' },
  'Finance & Accounting':    { bg: '#F0FDF4', border: '#BBF7D0', color: '#15803D' },
  'Engineering':             { bg: '#FFF7ED', border: '#FED7AA', color: '#C2410C' },
  'Legal & Compliance':      { bg: '#FDF4FF', border: '#E9D5FF', color: '#7E22CE' },
};

/* ── Share URLs ────────────────────────────────────────────────────────── */
function buildShareLinks(job) {
  const text = encodeURIComponent(`🚀 ${job.title} at ${job.company} — ${job.salary} | Apply via Infinity Solutions`);
  const url  = encodeURIComponent(window.location.origin + `/jobs.html?job=${job.id}`);
  return {
    whatsapp: `https://wa.me/?text=${text}%20${url}`,
    linkedin:  `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
    facebook:  `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`,
    copy:      window.location.origin + `/jobs.html?job=${job.id}`,
  };
}

/* ── Render job card ───────────────────────────────────────────────────── */
function renderJobCard(job) {
  const s = SECTOR_STYLE[job.sector] || SECTOR_STYLE['Technology'];
  const share = buildShareLinks(job);
  const date = new Date(job.posted).toLocaleDateString('en-CA', { month: 'short', day: 'numeric' });

  return `
  <article class="job-card" data-id="${job.id}" data-sector="${job.sector}" data-type="${job.type}" data-remote="${job.remote}">
    ${job.hot ? '<div class="jc-hot-badge">🔥 Hot Role</div>' : ''}
    <div class="jc-header">
      <div class="jc-logo">${job.companyLogo}</div>
      <div class="jc-meta-top">
        <div class="jc-title">${job.title}</div>
        <div class="jc-company">${job.company}</div>
      </div>
      <div class="jc-match">
        <span class="jc-match-pct">${job.match}%</span>
        <span class="jc-match-label">AI MATCH</span>
      </div>
    </div>

    <div class="jc-tags">
      <span class="sector-badge" style="background:${s.bg};border-color:${s.border};color:${s.color}">${job.sector}</span>
      ${job.tags.map(t => `<span class="jc-tag">${t}</span>`).join('')}
    </div>

    <p class="jc-desc">${job.desc}</p>

    <div class="jc-info">
      <span class="jc-info-item">
        <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
        ${job.location}
      </span>
      <span class="jc-info-item">
        <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        ${job.type}
      </span>
      ${job.remote ? '<span class="jc-info-item jc-remote">⚡ Remote OK</span>' : ''}
      <span class="jc-info-item">
        <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        ${job.salary}
      </span>
    </div>

    <div class="jc-footer">
      <span class="jc-posted">Posted ${date}</span>
      <div class="jc-actions">
        <!-- Share popover -->
        <div class="share-popover">
          <button class="share-btn" title="Share this job" aria-label="Share job">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          </button>
          <div class="share-menu">
            <div class="share-menu-title">Share this role</div>
            <a class="share-link" href="${share.whatsapp}" target="_blank" rel="noopener">
              <span class="share-icon share-whatsapp">💬</span> WhatsApp
            </a>
            <a class="share-link" href="${share.linkedin}" target="_blank" rel="noopener">
              <span class="share-icon share-linkedin">🔗</span> LinkedIn
            </a>
            <a class="share-link" href="${share.facebook}" target="_blank" rel="noopener">
              <span class="share-icon share-facebook">👥</span> Facebook
            </a>
            <button class="share-link share-copy-btn" data-url="${share.copy}">
              <span class="share-icon share-copy">📋</span> Copy Link
            </button>
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="openJobApply('${job.id}','${job.title}','${job.company}')">Apply Now →</button>
      </div>
    </div>
  </article>`;
}

/* ── Filter & render ───────────────────────────────────────────────────── */
let activeFilters = { sector: '', type: '', remote: null, search: '' };

function filterJobs(filters) {
  return JOBS.filter(j => {
    if (filters.sector && j.sector !== filters.sector) return false;
    if (filters.type   && j.type   !== filters.type)   return false;
    if (filters.remote !== null && j.remote !== filters.remote) return false;
    if (filters.search) {
      const q = filters.search.toLowerCase();
      if (![j.title, j.company, j.location, j.desc, ...j.tags].some(s => s.toLowerCase().includes(q))) return false;
    }
    return true;
  });
}

function renderJobsList() {
  const list    = document.getElementById('jobs-list');
  const countEl = document.getElementById('results-count');
  if (!list) return;

  const results = filterJobs(activeFilters);
  if (countEl) countEl.textContent = `${results.length} roles found`;

  if (!results.length) {
    list.innerHTML = `
      <div style="text-align:center;padding:80px 20px;color:var(--text-mid)">
        <div style="font-size:3rem;margin-bottom:16px">🔍</div>
        <h3 style="font-size:1.2rem;font-weight:700;color:var(--gray-700);margin-bottom:8px">No roles found</h3>
        <p style="font-size:.9rem">Try adjusting your filters or search terms.</p>
      </div>`;
    return;
  }
  list.innerHTML = results.map(renderJobCard).join('');

  // Re-init share popovers for newly rendered cards
  if (window.initSharePopovers) window.initSharePopovers();

  // Re-init share popovers inline
  list.querySelectorAll('.share-popover').forEach(wrap => {
    const btn  = wrap.querySelector('.share-btn');
    const menu = wrap.querySelector('.share-menu');
    if (!btn || !menu) return;
    btn.addEventListener('click', e => {
      e.stopPropagation();
      document.querySelectorAll('.share-menu.open').forEach(m => { if (m !== menu) m.classList.remove('open'); });
      menu.classList.toggle('open');
    });
  });
  list.querySelectorAll('.share-copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = btn.dataset.url;
      navigator.clipboard.writeText(url).then(() => {
        const orig = btn.innerHTML;
        btn.innerHTML = `<span class="share-icon share-copy">✓</span> Copied!`;
        setTimeout(() => { btn.innerHTML = orig; }, 2000);
      });
    });
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.share-menu.open').forEach(m => m.classList.remove('open'));
  }, { once: false });
}

/* ── Wire filters on page load ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  renderJobsList();

  // Search input
  const searchEl = document.getElementById('job-search');
  if (searchEl) {
    searchEl.addEventListener('input', e => { activeFilters.search = e.target.value; renderJobsList(); });
  }

  // Filter pills
  document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.filter;
      const val = btn.dataset.val;

      if (key === 'remote') {
        const boolVal = val === 'true' ? true : val === '' ? null : false;
        activeFilters.remote = activeFilters.remote === boolVal ? null : boolVal;
      } else {
        activeFilters[key] = activeFilters[key] === val ? '' : val;
      }

      // Update active states
      document.querySelectorAll(`[data-filter="${key}"]`).forEach(b => b.classList.remove('active'));
      if (val === '' || (key === 'remote' && activeFilters.remote === null)) {
        document.querySelector(`[data-filter="${key}"][data-val=""]`)?.classList.add('active');
      } else {
        btn.classList.add('active');
      }

      renderJobsList();
    });
  });

  // Clear all
  const clearBtn = document.getElementById('clear-filters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      activeFilters = { sector: '', type: '', remote: null, search: '' };
      if (searchEl) searchEl.value = '';
      document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('[data-filter][data-val=""]').forEach(b => b.classList.add('active'));
      renderJobsList();
    });
  }
});
