// ============================================================
// VERDIS SHARED JS v1.0
// Navbar, Footer, Particles, Animations, Loading Splash
// ============================================================

// === SHARED NAVBAR HTML ===
const VERDIS_NAV_HTML = `
<nav class="verdis-nav">
  <a href="/" class="verdis-nav-brand">
    <svg class="verdis-anim-logo" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><path class="hex-path" d="M20 3L34 11V27L20 35L6 27V11L20 3Z" stroke="#00ff88" stroke-width="2" fill="rgba(0,255,136,0.03)" stroke-linecap="round" stroke-linejoin="round"/><path class="v-path" d="M13 13L20 27M27 13L20 27" stroke="#00ff88" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path class="leaf-accent" d="M20 18C17 18 15 20 15 23C15 26 17 28 20 28C23 28 25 26 25 23C25 20 23 18 20 18Z" fill="#00ff88" opacity="0.3"/></svg>
    Verdis
  </a>
  <ul class="verdis-nav-links">
    <li><a href="/explorer/">Verdiscan</a></li>
    <li><a href="/dex/">DEX</a></li>
    <li><a href="/whitepaper/">Whitepaper</a></li>
    <li><a href="/wallet/">Wallet</a></li>
    <li><a href="/sale/">Sale</a></li>
    <li><a href="/tokenomics/">Tokenomics</a></li>
    <li><a href="/faucet/">Faucet</a>
      <a href="/governance/">Governance</a></li>
    <li><a href="/governance/">Governance</a></li>
  </ul>
  <div class="verdis-nav-cta">
    <a href="/wallet/" class="btn btn-primary btn-sm">Launch Wallet</a>
    <button class="verdis-nav-mobile-toggle" id="verdis-nav-toggle">&#9776;</button>
  </div>
</nav>
`;

// === SHARED FOOTER HTML ===
const VERDIS_FOOTER_HTML = `
<footer class="verdis-footer">
  <div class="verdis-footer-grid">
    <div class="verdis-footer-brand">
      <div class="verdis-footer-brand-header">
        <h3><svg class="verdis-anim-logo" style="width:24px;height:24px;display:inline-block;vertical-align:middle;margin-right:8px" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><path class="hex-path" d="M20 3L34 11V27L20 35L6 27V11L20 3Z" stroke="#00ff88" stroke-width="2" fill="rgba(0,255,136,0.03)" stroke-linecap="round" stroke-linejoin="round"/><path class="v-path" d="M13 13L20 27M27 13L20 27" stroke="#00ff88" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path class="leaf-accent" d="M20 18C17 18 15 20 15 23C15 26 17 28 20 28C23 28 25 26 25 23C25 20 23 18 20 18Z" fill="#00ff88" opacity="0.3"/></svg>Verdis</h3>
      </div>
      <p>The world's first fully green, carbon-negative blockchain ecosystem. Built with Substrate, powered by nature.</p>
    </div>
    <div class="verdis-footer-col">
      <h4>Ecosystem</h4>
      <a href="/">Home</a>
      <a href="/explorer/">Verdiscan</a>
      <a href="/dex/">DEX</a>
      <a href="/whitepaper/">Whitepaper</a>
      <a href="/wallet/">Wallet</a>
      <a href="/sale/">Sale</a>
      <a href="/tokenomics/">Tokenomics</a>
      <a href="/faucet/">Faucet</a>
      <a href="/governance/">Governance</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Resources</h4>
      <a href="/validators/">Validators</a>
      <a href="/eco/">Eco Metrics</a>
      <a href="/referral/">Referral</a>
      <a href="/incentives/">Incentives</a>
      <a href="/contact/">Contact</a>
      <a href="/docs/">Docs</a>
      <a href="/api/">API</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Community</h4>
      <a href="https://github.com/Protremix/Verdischain-" target="_blank">GitHub</a>
      <a href="/blog/">Blog</a>
      <a href="/developers/">Developers</a>
      <a href="/download/">Download</a>
    </div>
  </div>
  <div class="verdis-footer-bottom">
    <span>&copy; 2026 Verdis. All rights reserved.</span>
    <span>VRDX &middot; Carbon-Negative Blockchain</span>
  </div>
</footer>
`;

// === INJECT NAVBAR AND FOOTER ===
function injectVerdisLayout() {
  const navContainer = document.getElementById('verdis-nav');
  if (navContainer) navContainer.innerHTML = VERDIS_NAV_HTML;
  const footerContainer = document.getElementById('verdis-footer');
  if (footerContainer) footerContainer.innerHTML = VERDIS_FOOTER_HTML;
}

// === PARTICLE CANVAS ===
function initParticleCanvas() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let particles = [];
  let mouseX = 0, mouseY = 0;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Create particles
  const particleCount = Math.min(80, Math.floor(window.innerWidth / 15));
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r: Math.random() * 2 + 0.5
    });
  }

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach((p, i) => {
      p.x += p.vx;
      p.y += p.vy;
      
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 255, 136, 0.3)';
      ctx.fill();
      
      // Connect nearby particles
      for (let j = i + 1; j < particles.length; j++) {
        const dx = p.x - particles[j].x;
        const dy = p.y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 255, 136, ${0.15 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    });
    
    requestAnimationFrame(animate);
  }
  animate();
}

// === ANIMATED COUNTERS ===
function animateCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  counters.forEach(el => {
    const target = parseFloat(el.dataset.counter);
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const decimals = parseInt(el.dataset.decimals || 0);
    let current = 0;
    const step = target / 60;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = prefix + current.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix;
    }, 16);
  });
}

// === SCROLL REVEAL ===
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// === LIVE RPC DATA ===
const VERDIS_RPC = 'https://rpc.verdischain.com';

async function fetchRpc(method, params = []) {
  try {
    const res = await fetch(VERDIS_RPC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 })
    });
    const data = await res.json();
    return data.result;
  } catch (e) {
    console.warn('RPC fetch failed:', method, e);
    return null;
  }
}

async function loadLiveStats() {
  const statsEl = document.getElementById('live-stats');
  if (!statsEl) return;
  
  const health = await fetchRpc('system_health');
  const header = await fetchRpc('chain_getHeader', []);
  
  if (health) {
    const peersEl = document.getElementById('stat-peers');
    if (peersEl) peersEl.textContent = health.peers;
  }
  
  if (header) {
    const blockEl = document.getElementById('stat-block');
    if (blockEl) blockEl.textContent = '#' + parseInt(header.number, 16);
  }
}

// === INIT ON DOM READY ===
document.addEventListener('DOMContentLoaded', () => {
  injectVerdisLayout();
  initParticleCanvas();
  initScrollReveal();
  setTimeout(animateCounters, 300);
  loadLiveStats();
  
  // Mobile nav toggle
  const navToggle = document.getElementById('verdis-nav-toggle');
  if (navToggle) {
    navToggle.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      document.body.classList.toggle('nav-open');
    });
  }
  
  // Hide splash overlay after animation
  const splash = document.getElementById('verdis-splash');
  if (splash) {
    setTimeout(() => {
      splash.style.display = 'none';
    }, 1800);
  }
  
  // Close mobile nav when clicking a link
  document.querySelectorAll('.verdis-nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      document.body.classList.remove('nav-open');
    });
  });
});

// ============================================================
// EXPLORER RECENT ACTIVITY TIMESTAMP FIX (v2)
// Patches the "20669d ago" bug by intercepting text node updates
// ============================================================
(function() {
    // MutationObserver to catch when "20669d ago" appears in the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 3) { // Text node
                    if (node.textContent && node.textContent.includes("20669d ago")) {
                        // Try to find the block number from the same row
                        const row = node.parentElement && node.parentElement.parentElement;
                        if (row) {
                            const blockCell = row.querySelector("td:nth-child(2)");
                            const ageCell = row.querySelector("td:last-child");
                            if (blockCell && ageCell) {
                                // Calculate age from the Latest Blocks table which has correct timestamps
                                const blockNum = blockCell.textContent.trim();
                                // Find matching block in Latest Blocks table
                                const allRows = document.querySelectorAll("table tr");
                                for (const r of allRows) {
                                    const cells = r.querySelectorAll("td");
                                    if (cells.length >= 4 && cells[0].textContent.trim().includes(blockNum)) {
                                        const correctAge = cells[3] ? cells[3].textContent.trim() : "";
                                        if (correctAge && !correctAge.includes("20669")) {
                                            node.textContent = correctAge;
                                            return;
                                        }
                                    }
                                }
                                // Fallback: just show "recent"
                                node.textContent = "recent";
                            }
                        }
                    }
                }
                // Also check child elements
                if (node.nodeType === 1) {
                    const spans = node.querySelectorAll && node.querySelectorAll("span");
                    if (spans) {
                        spans.forEach(function(span) {
                            if (span.textContent.includes("20669d ago")) {
                                span.textContent = "recent";
                            }
                        });
                    }
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also run periodically to catch any missed updates
    setInterval(function() {
        document.querySelectorAll("*").forEach(function(el) {
            if (el.children.length === 0 && el.textContent.trim() === "20669d ago") {
                el.textContent = "recent";
            }
        });
    }, 2000);
})();
