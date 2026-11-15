/* ═══════════════════════════════════════════════════════════════════════════
   INFINITY STAFFING — main.js
   React-ready: all logic is pure functions / event-driven, no globals polluted
   ═══════════════════════════════════════════════════════════════════════════ */

'use strict';

/* ── Navbar scroll ─────────────────────────────────────────────────────── */
export function initNavbar() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  const update = () => nav.classList.toggle('scrolled', window.scrollY > 20);
  window.addEventListener('scroll', update, { passive: true });
  update();
}

/* ── Mobile menu ───────────────────────────────────────────────────────── */
export function initMobileMenu() {
  const burger = document.getElementById('burger');
  const drawer = document.getElementById('drawer');
  if (!burger || !drawer) return;
  burger.addEventListener('click', () => {
    const open = drawer.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });
  drawer.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => drawer.classList.remove('open'))
  );
}

/* ── Share popover ─────────────────────────────────────────────────────── */
export function initSharePopovers() {
  document.querySelectorAll('.share-popover').forEach(wrap => {
    const btn  = wrap.querySelector('.share-btn');
    const menu = wrap.querySelector('.share-menu');
    if (!btn || !menu) return;

    btn.addEventListener('click', e => {
      e.stopPropagation();
      document.querySelectorAll('.share-menu.open').forEach(m => { if (m !== menu) m.classList.remove('open'); });
      menu.classList.toggle('open');
    });
  });

  // Copy link
  document.querySelectorAll('.share-copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = btn.dataset.url || window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        const orig = btn.innerHTML;
        btn.innerHTML = `<span class="share-icon share-copy">✓</span> Copied!`;
        setTimeout(() => { btn.innerHTML = orig; }, 2000);
      });
    });
  });

  document.addEventListener('click', () => {
    document.querySelectorAll('.share-menu.open').forEach(m => m.classList.remove('open'));
  });
}

/* ── Animate on scroll ─────────────────────────────────────────────────── */
export function initScrollAnimations() {
  if (!('IntersectionObserver' in window)) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in-view');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('[data-animate]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity .6s ease ${el.dataset.delay || '0'}ms, transform .6s ease ${el.dataset.delay || '0'}ms`;
    obs.observe(el);
  });

  document.addEventListener('animationend', (e) => {
    if (e.target.classList.contains('in-view')) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'none';
    }
  });
}

// Simpler in-view via class
document.addEventListener('DOMContentLoaded', () => {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('[data-animate]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity .6s ease ${el.dataset.delay || 0}ms, transform .6s ease ${el.dataset.delay || 0}ms`;
    obs.observe(el);
  });
});

/* ── Industry tabs ─────────────────────────────────────────────────────── */
export function initIndustryTabs() {
  document.querySelectorAll('.ind-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const id = tab.dataset.target;
      document.querySelectorAll('.ind-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.ind-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById(id);
      if (panel) panel.classList.add('active');
    });
  });
}

/* ── Search tabs ───────────────────────────────────────────────────────── */
export function initSearchTabs() {
  document.querySelectorAll('.stab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.stab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });
}

/* ── Counter animation ─────────────────────────────────────────────────── */
export function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el    = e.target;
      const target = parseInt(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      const dur   = 1800;
      const start = performance.now();
      const tick  = (now) => {
        const p = Math.min((now - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.floor(ease * target) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      obs.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(c => obs.observe(c));
}

/* ── Init all ──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initMobileMenu();
  initSharePopovers();
  initIndustryTabs();
  initSearchTabs();
  initCounters();
});
