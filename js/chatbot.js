/* ═══════════════════════════════════════════════════════
   INFINITY AI CHATBOT — Powered by Claude API
   ═══════════════════════════════════════════════════════ */
'use strict';

const BOT_SYSTEM = `You are Aria, the AI recruitment assistant for Infinity Solutions — Canada's AI-powered staffing platform based in Toronto.

Your role: Help visitors find jobs, understand our services, and connect with our team.

Key facts about Infinity Solutions:
- AI-powered talent platform matching professionals in: IT & Technology, Artificial Intelligence, Data & Analytics, Engineering (Mechanical, Electrical, Civil, Automotive, Chemical), Legal & Compliance (Corporate Lawyers, In-House Counsel, Compliance Officers, Privacy Lawyers), Finance & Accounting
- Based in Toronto, Canada
- Contact: contact form on our website (we don't share email/phone publicly)
- AI Match Score: every candidate gets a % match rating across 40+ parameters
- 500+ placements, 98% client satisfaction, 24h AI shortlist turnaround
- Services: Contract hire, Permanent hire, Managed Solutions
- Key sectors: IT & Technology, Artificial Intelligence, Data & Analytics, Finance & Accounting

Rules:
- Be warm, helpful, concise (2-3 sentences max per reply)
- NEVER share email addresses or phone numbers — direct people to the contact page
- For job applications: direct to jobs.html
- For employer enquiries: direct to contact-ai.html
- If asked about salary: give general market ranges, never commit to specific numbers
- If asked something you don't know: say you'll have a specialist follow up
- Use emojis sparingly (1 per message max)
- Always offer a follow-up action (e.g. "Want me to show you our open IT roles?")`;

const QUICK_REPLIES_INIT = [
  "Find me a job 🔍",
  "I want to hire talent",
  "How does AI matching work?",
  "What sectors do you cover?"
];

class InfinityChat {
  constructor() {
    this.history = [];
    this.isOpen = false;
    this.isTyping = false;
    this.unreadCount = 1;
    this.inject();
    this.bindEvents();
    // Greet after short delay
    setTimeout(() => this.showGreeting(), 800);
  }

  inject() {
    // Launcher
    document.body.insertAdjacentHTML('beforeend', `
      <button class="chat-launcher" id="chatLauncher" aria-label="Open AI chat assistant">
        <svg class="icon-chat" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <svg class="icon-close" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2.5">
          <path d="M18 6 6 18M6 6l12 12"/>
        </svg>
        <div class="chat-launcher-dot" id="chatDot">1</div>
      </button>

      <div class="chat-window" id="chatWindow" role="dialog" aria-label="Infinity Solutions AI Chat">
        <div class="chat-header">
          <div class="chat-header-av">🤖</div>
          <div class="chat-header-info">
            <div class="chat-header-name">Aria — AI Assistant</div>
            <div class="chat-header-status">
              <div class="chat-status-dot"></div>
              Online · Typically replies instantly
            </div>
          </div>
          <div class="chat-header-badge">✦ AI</div>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input-area">
          <textarea class="chat-input" id="chatInput" placeholder="Ask Aria anything..." rows="1" maxlength="500"></textarea>
          <button class="chat-send" id="chatSend" aria-label="Send message" disabled>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
        <div class="chat-powered">⚡ Powered by Infinity AI · <a href="contact-ai.html" style="color:#3B82F6">Talk to a human</a></div>
      </div>
    `);
  }

  bindEvents() {
    const launcher = document.getElementById('chatLauncher');
    const input    = document.getElementById('chatInput');
    const sendBtn  = document.getElementById('chatSend');

    launcher.addEventListener('click', () => this.toggle());

    input.addEventListener('input', () => {
      sendBtn.disabled = !input.value.trim();
      // Auto-resize
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); }
    });

    sendBtn.addEventListener('click', () => this.send());
  }

  toggle() {
    this.isOpen = !this.isOpen;
    document.getElementById('chatLauncher').classList.toggle('open', this.isOpen);
    document.getElementById('chatWindow').classList.toggle('open', this.isOpen);
    if (this.isOpen) {
      // Clear unread
      const dot = document.getElementById('chatDot');
      dot.style.display = 'none';
      this.unreadCount = 0;
      document.getElementById('chatInput').focus();
      this.scrollBottom();
    }
  }

  showGreeting() {
    this.addBotMsg("Hi there! 👋 I'm **Aria**, Infinity Solutions AI assistant. Whether you're looking for your next role or need to hire top talent fast — I'm here to help!");
    setTimeout(() => this.addQuickReplies(QUICK_REPLIES_INIT), 600);
  }

  addBotMsg(text, withTime = true) {
    const msgs = document.getElementById('chatMessages');
    const now  = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const html = this.formatText(text);
    const el   = document.createElement('div');
    el.className = 'msg bot';
    el.innerHTML = `
      <div class="msg-av">🤖</div>
      <div>
        <div class="msg-bubble">${html}</div>
        ${withTime ? `<div class="msg-time">${now}</div>` : ''}
      </div>`;
    msgs.appendChild(el);
    this.scrollBottom();
  }

  addUserMsg(text) {
    const msgs = document.getElementById('chatMessages');
    const now  = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const el   = document.createElement('div');
    el.className = 'msg user';
    el.innerHTML = `
      <div>
        <div class="msg-bubble">${this.escapeHtml(text)}</div>
        <div class="msg-time">${now}</div>
      </div>`;
    msgs.appendChild(el);
    this.scrollBottom();
  }

  addQuickReplies(options) {
    const msgs = document.getElementById('chatMessages');
    const wrap = document.createElement('div');
    wrap.className = 'msg bot';
    wrap.innerHTML = `<div class="msg-av" style="opacity:0"></div><div class="quick-replies">${
      options.map(o => `<button class="qr-btn">${o}</button>`).join('')
    }</div>`;
    msgs.appendChild(wrap);
    wrap.querySelectorAll('.qr-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        wrap.remove();
        this.handleUserInput(btn.textContent);
      });
    });
    this.scrollBottom();
  }

  showTyping() {
    const msgs = document.getElementById('chatMessages');
    const el   = document.createElement('div');
    el.className = 'msg bot'; el.id = 'typingIndicator';
    el.innerHTML = `<div class="msg-av">🤖</div><div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
    msgs.appendChild(el);
    this.scrollBottom();
    return el;
  }

  removeTyping() {
    document.getElementById('typingIndicator')?.remove();
  }

  async send() {
    const input = document.getElementById('chatInput');
    const text  = input.value.trim();
    if (!text || this.isTyping) return;
    input.value = ''; input.style.height = 'auto';
    document.getElementById('chatSend').disabled = true;
    this.handleUserInput(text);
  }

  async handleUserInput(text) {
    this.addUserMsg(text);
    // Remove any quick replies
    document.querySelectorAll('.quick-replies').forEach(el => el.closest('.msg')?.remove());

    this.isTyping = true;
    const typingEl = this.showTyping();

    // Build history
    this.history.push({ role: 'user', content: text });

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 300,
          system: BOT_SYSTEM,
          messages: this.history.slice(-12), // keep last 12 for context
        })
      });

      const data = await response.json();
      const reply = data.content?.[0]?.text || "I'm having a little trouble connecting right now. Please try again or visit our contact page!";
      this.history.push({ role: 'assistant', content: reply });

      this.removeTyping();
      this.addBotMsg(reply);

      // Context-aware quick replies
      const lower = text.toLowerCase();
      if (lower.includes('job') || lower.includes('find') || lower.includes('role') || lower.includes('work')) {
        setTimeout(() => this.addQuickReplies(['Browse all jobs', 'Remote only', 'AI & Tech roles', 'Finance roles']), 400);
      } else if (lower.includes('hire') || lower.includes('talent') || lower.includes('recruit') || lower.includes('employer')) {
        setTimeout(() => this.addQuickReplies(['How does AI matching work?', 'How fast can you hire?', 'Contact a recruiter']), 400);
      } else if (lower.includes('contact') || lower.includes('recruiter') || lower.includes('human') || lower.includes('talk')) {
        setTimeout(() => this.addQuickReplies(['Open contact page', 'How does AI matching work?']), 400);
      }

      // Handle navigation intents
      if (reply.toLowerCase().includes('contact') && lower.includes('contact')) {
        setTimeout(() => {
          const linkEl = document.createElement('div');
          linkEl.className = 'msg bot';
          linkEl.innerHTML = `<div class="msg-av" style="opacity:0"></div><a href="contact-ai.html" style="display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#2563EB,#1D4ED8);color:#fff;border-radius:10px;padding:9px 18px;font-size:.83rem;font-weight:700;font-family:'Plus Jakarta Sans',sans-serif;text-decoration:none">→ Open Contact Page</a>`;
          document.getElementById('chatMessages').appendChild(linkEl);
          this.scrollBottom();
        }, 300);
      }
      if (lower.includes('job') || lower.includes('browse') || lower.includes('roles')) {
        setTimeout(() => {
          const linkEl = document.createElement('div');
          linkEl.className = 'msg bot';
          linkEl.innerHTML = `<div class="msg-av" style="opacity:0"></div><a href="jobs.html" style="display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#2563EB,#1D4ED8);color:#fff;border-radius:10px;padding:9px 18px;font-size:.83rem;font-weight:700;font-family:'Plus Jakarta Sans',sans-serif;text-decoration:none">→ View All Jobs</a>`;
          document.getElementById('chatMessages').appendChild(linkEl);
          this.scrollBottom();
        }, 300);
      }

    } catch (err) {
      this.removeTyping();
      this.addBotMsg("Sorry, I'm having trouble right now. Please visit our [contact page](contact-ai.html) and a recruiter will be in touch within 24 hours!");
    }

    this.isTyping = false;

    // Bump unread if window is closed
    if (!this.isOpen) {
      this.unreadCount++;
      const dot = document.getElementById('chatDot');
      dot.textContent = this.unreadCount;
      dot.style.display = 'flex';
    }
  }

  formatText(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color:#2563EB;font-weight:600">$1</a>')
      .replace(/\n/g, '<br>');
  }

  escapeHtml(text) {
    return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  scrollBottom() {
    const msgs = document.getElementById('chatMessages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  }
}

// Init when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window._infinityChat = new InfinityChat();
});
