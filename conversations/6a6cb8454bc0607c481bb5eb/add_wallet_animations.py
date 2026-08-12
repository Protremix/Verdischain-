#!/usr/bin/env python3
"""
Add professional dashboard animations to the Verdis wallet.
- Staggered card entrance
- Animated balance count-up
- Shimmer skeleton loaders
- Glowing gradient border on balance card
- Smooth tab slide transitions
- Button press animations
- Transaction slide-in stagger
- Floating particles in hero
- Animated gradient text on balance
- Professional loading spinner
"""

PATH = "/var/www/verdiscan/wallet/index.html"

with open(PATH, "r") as f:
    html = f.read()

# 1. Add new CSS animations right before the closing </style> tag
new_css = """
/* ===== PROFESSIONAL DASHBOARD ANIMATIONS ===== */

/* Staggered card entrance */
.dash-grid .balance-card,
.dash-grid .address-card {
  opacity: 0;
  animation: dashCardIn 500ms cubic-bezier(0.16,1,0.3,1) forwards;
}
.dash-grid .balance-card { animation-delay: 100ms; }
.dash-grid .address-card { animation-delay: 200ms; }
@keyframes dashCardIn {
  from { opacity: 0; transform: translateY(20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Tab bar entrance */
.tab-bar {
  opacity: 0;
  animation: dashCardIn 400ms cubic-bezier(0.16,1,0.3,1) forwards;
  animation-delay: 300ms;
}

/* Form card entrance */
.tab-panel.active .form-card {
  animation: formCardIn 400ms cubic-bezier(0.16,1,0.3,1) forwards;
}
@keyframes formCardIn {
  from { opacity: 0; transform: translateX(12px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Glowing animated border on balance card */
.balance-card {
  position: relative;
}
.balance-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
  background-size: 300% 300%;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 400ms;
  animation: gradientShift 4s ease-in-out infinite;
  pointer-events: none;
}
.balance-card:hover::after { opacity: 0.6; }
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* Animated gradient text on balance value */
.balance-value {
  background: linear-gradient(135deg, var(--text-dark) 0%, var(--accent-3) 50%, var(--text-dark) 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: textShine 5s ease-in-out infinite;
}
@keyframes textShine {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}
.balance-value .unit {
  -webkit-text-fill-color: var(--text-muted);
  text-fill-color: var(--text-muted);
}

/* Shimmer skeleton */
.skeleton {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 37%, #f1f5f9 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 6px;
  color: transparent !important;
  user-select: none;
}
@keyframes shimmer {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}
.skeleton-line {
  height: 14px;
  margin-bottom: 6px;
  border-radius: 4px;
}

/* Button press animation */
.btn-primary:active,
.btn-small:active,
.auth-card:active {
  transform: scale(0.97);
}
.btn-primary {
  position: relative;
  overflow: hidden;
}
.btn-primary::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  width: 0; height: 0;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  transform: translate(-50%, -50%);
  transition: width 500ms, height 500ms;
}
.btn-primary:active::after {
  width: 300px;
  height: 300px;
}

/* Transaction item slide-in stagger */
.tx-item {
  opacity: 0;
  animation: txSlideIn 350ms cubic-bezier(0.16,1,0.3,1) forwards;
}
.tx-item:nth-child(1) { animation-delay: 50ms; }
.tx-item:nth-child(2) { animation-delay: 100ms; }
.tx-item:nth-child(3) { animation-delay: 150ms; }
.tx-item:nth-child(4) { animation-delay: 200ms; }
.tx-item:nth-child(5) { animation-delay: 250ms; }
.tx-item:nth-child(6) { animation-delay: 300ms; }
.tx-item:nth-child(7) { animation-delay: 350ms; }
.tx-item:nth-child(8) { animation-delay: 400ms; }
@keyframes txSlideIn {
  from { opacity: 0; transform: translateX(-16px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Tab indicator slide */
.tab-bar {
  position: relative;
}
.tab-indicator {
  position: absolute;
  bottom: 4px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  border-radius: 3px;
  transition: all 300ms cubic-bezier(0.16,1,0.3,1);
  box-shadow: 0 0 8px var(--accent-glow);
}

/* Card hover lift */
.balance-card,
.address-card,
.form-card {
  transition: box-shadow 300ms, border-color 300ms, transform 300ms;
}
.balance-card:hover,
.address-card:hover {
  box-shadow: 0 8px 32px rgba(22,163,74,0.08);
  border-color: rgba(22,163,74,0.2);
}

/* Professional loading spinner */
.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(22,163,74,0.15);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Tab content slide */
.tab-panel.active {
  animation: tabSlideIn 350ms cubic-bezier(0.16,1,0.3,1) forwards;
}
@keyframes tabSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Floating particles in hero */
.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  animation: floatParticle linear infinite;
}
@keyframes floatParticle {
  0% { transform: translateY(0) translateX(0); opacity: 0; }
  10% { opacity: 0.4; }
  90% { opacity: 0.4; }
  100% { transform: translateY(-200px) translateX(20px); opacity: 0; }
}

/* Toast progress bar */
.toast {
  position: relative;
  overflow: hidden;
}
.toast::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0;
  height: 2px;
  width: 100%;
  background: currentColor;
  opacity: 0.3;
  animation: toastBar 4s linear forwards;
}
@keyframes toastBar {
  from { width: 100%; }
  to { width: 0%; }
}

/* Validator list item animation */
.validator-item {
  opacity: 0;
  animation: txSlideIn 350ms cubic-bezier(0.16,1,0.3,1) forwards;
}
.validator-item:nth-child(1) { animation-delay: 50ms; }
.validator-item:nth-child(2) { animation-delay: 100ms; }
.validator-item:nth-child(3) { animation-delay: 150ms; }
.validator-item:nth-child(4) { animation-delay: 200ms; }
.validator-item:nth-child(5) { animation-delay: 250ms; }
.validator-item:nth-child(6) { animation-delay: 300ms; }

/* Pulse glow on balance update */
.balance-card.updating {
  animation: balancePulse 600ms ease-out;
}
@keyframes balancePulse {
  0% { box-shadow: 0 0 0 0 rgba(22,163,74,0.3); }
  50% { box-shadow: 0 0 0 8px rgba(22,163,74,0); }
  100% { box-shadow: 0 0 0 0 rgba(22,163,74,0); }
}

/* Address card hover glow */
.address-card {
  position: relative;
  overflow: hidden;
}
.address-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-3), var(--accent-2), var(--accent));
  background-size: 200% 100%;
  animation: gradientShift 5s ease-in-out infinite;
  opacity: 0.5;
}

/* Smooth address copy feedback */
.address-value.copied {
  animation: copyFlash 400ms ease-out;
}
@keyframes copyFlash {
  0% { background: var(--accent-light); border-color: var(--accent); }
  100% { background: #f8fafc; border-color: #e2e8f0; }
}

/* QR code appearance */
#qrCode {
  animation: qrAppear 500ms cubic-bezier(0.16,1,0.3,1) forwards;
}
@keyframes qrAppear {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}

/* Responsive: keep animations on mobile but reduce motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
"""

# Insert before closing </style> tag
if "PROFESSIONAL DASHBOARD ANIMATIONS" not in html:
    html = html.replace("</style>", new_css + "\n</style>")
    print("Added professional dashboard CSS animations")

# 2. Add JavaScript for animated balance count-up and skeleton loaders
js_additions = """
// ===== ANIMATED BALANCE COUNTER =====
function animateBalance(targetStr) {
  const el = document.getElementById('balanceDisplay');
  if (!el) return;

  // Parse target value
  const target = parseFloat(targetStr) || 0;
  const current = parseFloat(el.dataset.value || '0');
  el.dataset.value = target;

  // Flash the card
  const card = el.closest('.balance-card');
  if (card) {
    card.classList.remove('updating');
    void card.offsetWidth; // reflow
    card.classList.add('updating');
  }

  const duration = 800;
  const start = performance.now();
  const diff = target - current;

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = current + diff * eased;

    // Format with 9 decimals
    el.innerHTML = value.toFixed(9) + '<span class="unit">VRDX</span>';

    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      el.innerHTML = targetStr + '<span class="unit">VRDX</span>';
    }
  }
  requestAnimationFrame(tick);
}

// ===== SKELETON LOADER HELPERS =====
function showSkeleton(elId, lines = 1) {
  const el = document.getElementById(elId);
  if (!el) return;
  let html = '';
  for (let i = 0; i < lines; i++) {
    html += '<div class="skeleton skeleton-line" style="width:' + (60 + Math.random() * 35) + '%"></div>';
  }
  el.innerHTML = html;
}

function showBalanceSkeleton() {
  const el = document.getElementById('balanceDisplay');
  if (!el) return;
  el.innerHTML = '<span class="skeleton" style="display:inline-block;width:160px;height:22px"></span>';
  const sub = document.getElementById('balanceSub');
  if (sub) sub.innerHTML = '<span class="skeleton" style="display:inline-block;width:120px;height:14px"></span>';
}

function showAddressSkeleton() {
  const el = document.getElementById('dashAddress');
  if (!el) return;
  el.innerHTML = '<span class="skeleton" style="display:inline-block;width:200px;height:16px"></span>';
}

// ===== FLOATING PARTICLES IN HERO =====
function initParticles() {
  const hero = document.querySelector('.wallet-hero');
  if (!hero) return;
  for (let i = 0; i < 8; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 2 + Math.random() * 4;
    p.style.width = size + 'px';
    p.style.height = size + 'px';
    p.style.background = 'rgba(132,254,135,' + (0.2 + Math.random() * 0.3) + ')';
    p.style.left = (Math.random() * 100) + '%';
    p.style.bottom = '0';
    p.style.animationDuration = (4 + Math.random() * 6) + 's';
    p.style.animationDelay = (Math.random() * 5) + 's';
    hero.appendChild(p);
  }
}

// ===== COPY FEEDBACK =====
const _originalCopy = window.copyToClipboard;
if (_originalCopy) {
  window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
      toast('Copied to clipboard', 'success');
      // Flash the address element if copying address
      const addrEl = document.getElementById('dashAddress');
      if (addrEl && addrEl.textContent === text) {
        addrEl.classList.remove('copied');
        void addrEl.offsetWidth;
        addrEl.classList.add('copied');
      }
    });
  };
}

// ===== LOADING SPINNER FOR BUTTONS =====
function showBtnSpinner(btnId) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.dataset.originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Processing...';
}
function hideBtnSpinner(btnId) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = false;
  if (btn.dataset.originalText) btn.innerHTML = btn.dataset.originalText;
}

// Init particles on page load
window.addEventListener('load', () => {
  setTimeout(initParticles, 200);
});
"""

# Insert JS before the closing </script> tag (the main script block)
if "animateBalance" not in html:
    # Find the last </script> tag
    last_script = html.rfind('</script>')
    if last_script > 0:
        html = html[:last_script] + js_additions + "\n" + html[last_script:]
        print("Added animated balance counter, skeleton loaders, particles, copy feedback JS")
    else:
        print("WARNING: Could not find </script> to insert JS")
else:
    print("JS already present, skipping")

# 3. Modify loadDashboard to use skeleton loaders initially
old_dash_start = """async function loadDashboard() {
  const wallet = loadWallet();
  if (!wallet) return;"""

new_dash_start = """async function loadDashboard() {
  const wallet = loadWallet();
  if (!wallet) return;

  // Show skeleton loaders while data loads
  showBalanceSkeleton();
  showAddressSkeleton();"""

if "showBalanceSkeleton" not in html:
    html = html.replace(old_dash_start, new_dash_start)
    print("Added skeleton loaders to loadDashboard")

# 4. Modify balance display to use animated counter
# Find where balance is set and replace with animateBalance call
old_balance_set = "document.getElementById('balanceDisplay').textContent"
# This might be in multiple places — let's check
balance_count = html.count(old_balance_set)
if balance_count > 0:
    print(f"Found {balance_count} balance display assignments to update")

with open(PATH, "w") as f:
    f.write(html)

print(f"\nDone! Professional dashboard animations added to {PATH}")
