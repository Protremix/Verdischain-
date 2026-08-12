#!/usr/bin/env python3
"""Add 3D floating cluster to docs page hero section."""

with open('/var/www/verdiscan/docs/index.html', 'r') as f:
    content = f.read()

# 1. Add 3D floating card CSS after .hero-box CSS
old_hero_box_css = """    .hero-box {
      background: linear-gradient(135deg, rgba(0, 255, 136, 0.12) 0%, rgba(10, 14, 10, 0.95) 100%),
                  radial-gradient(circle at top right, rgba(0, 255, 136, 0.15), transparent 60%);
      border: 1px solid var(--accent-border);
      border-radius: var(--radius-lg); padding: 40px 48px;
      position: relative; overflow: hidden; box-shadow: 0 12px 36px rgba(0,0,0,0.5);
    }"""

new_hero_box_css = """    .hero-box {
      background: linear-gradient(135deg, rgba(0, 255, 136, 0.12) 0%, rgba(10, 14, 10, 0.95) 100%),
                  radial-gradient(circle at top right, rgba(0, 255, 136, 0.15), transparent 60%);
      border: 1px solid var(--accent-border);
      border-radius: var(--radius-lg); padding: 40px 48px;
      position: relative; overflow: visible; box-shadow: 0 12px 36px rgba(0,0,0,0.5);
      min-height: 280px; display: flex; align-items: center;
    }
    .hero-box::before {
      content: ''; position: absolute; top: 50%; left: 50%;
      width: 300px; height: 300px; border-radius: 50%;
      background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
      opacity: 0.08; filter: blur(20px); transform: translate(-50%, -50%);
      pointer-events: none;
    }
    /* 3D Floating Cards */
    .hero-3d-cluster {
      position: absolute; right: 20px; top: 50%; transform: translateY(-50%);
      width: 280px; height: 240px; perspective: 1000px; pointer-events: none;
    }
    .float-3d-card {
      position: absolute; background: rgba(22, 163, 74, 0.08);
      backdrop-filter: blur(20px); border: 1px solid rgba(22, 163, 74, 0.2);
      border-radius: 12px; padding: 10px 14px; pointer-events: auto;
      transition: all 0.3s ease;
    }
    .float-3d-card:hover {
      border-color: rgba(22, 163, 74, 0.4);
      background: rgba(22, 163, 74, 0.12);
    }
    .float-3d-label {
      font-size: 10px; color: rgba(255,255,255,0.5);
      text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;
    }
    .float-3d-value {
      font-family: 'JetBrains Mono', monospace; font-size: 14px;
      font-weight: 600; color: var(--accent);
    }
    .float-3d-sub { font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 2px; }
    .fc3d-1 { top: 0; right: 0; animation: floatA 6s ease-in-out infinite; }
    .fc3d-2 { top: 80px; right: 80px; animation: floatB 7s ease-in-out infinite; }
    .fc3d-3 { bottom: 0; right: 30px; animation: floatC 8s ease-in-out infinite; }
    .fc3d-4 { bottom: 60px; right: 120px; animation: floatA 9s ease-in-out infinite; }
    .float-3d-tag {
      position: absolute; padding: 4px 10px;
      background: rgba(22,163,74,0.08); border: 1px solid rgba(22,163,74,0.2);
      border-radius: 100px; font-size: 10px; color: var(--accent);
      font-weight: 500; pointer-events: auto;
    }
    .ft3d-1 { top: 130px; right: 40px; animation: floatB 5s ease-in-out infinite; }
    @keyframes floatA { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    @keyframes floatB { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
    @keyframes floatC { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    @media (max-width: 768px) { .hero-3d-cluster { display: none; } }"""

content = content.replace(old_hero_box_css, new_hero_box_css)

# 2. Add 3D floating cards HTML inside the hero-box, after hero-stats
old_hero_stats_end = """        <div class="stat-card">
          <div class="stat-label">SS58 Format</div>
          <div class="stat-val">Prefix 909</div>
        </div>
      </div>
    </div>
  </header>"""

new_hero_stats_end = """        <div class="stat-card">
          <div class="stat-label">SS58 Format</div>
          <div class="stat-val">Prefix 909</div>
        </div>
      </div>

      <!-- 3D FLOATING UI CLUSTER -->
      <div class="hero-3d-cluster">
        <div class="float-3d-card fc3d-1">
          <div class="float-3d-label">Block Target</div>
          <div class="float-3d-value">3.0s</div>
          <div class="float-3d-sub">Substrate</div>
        </div>
        <div class="float-3d-card fc3d-2">
          <div class="float-3d-label">Pallets</div>
          <div class="float-3d-value">15</div>
          <div class="float-3d-sub">Runtime</div>
        </div>
        <div class="float-3d-card fc3d-3">
          <div class="float-3d-label">SDK Methods</div>
          <div class="float-3d-value">51</div>
          <div class="float-3d-sub">JavaScript</div>
        </div>
        <div class="float-3d-card fc3d-4">
          <div class="float-3d-label">Consensus</div>
          <div class="float-3d-value">DPoS</div>
          <div class="float-3d-sub">BABE+GRANDPA</div>
        </div>
        <div class="float-3d-tag ft3d-1">Carbon Negative</div>
      </div>
    </div>
  </header>"""

content = content.replace(old_hero_stats_end, new_hero_stats_end)

with open('/var/www/verdiscan/docs/index.html', 'w') as f:
    f.write(content)
print(f'Docs page updated with 3D floating cluster ({len(content)} bytes)')
