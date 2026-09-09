#!/usr/bin/env python
"""Add a network switcher to the explorer header (mainnet / testnet / devnet).

Constraint from the user: do not touch the logo or the design. So this adds a control
that inherits the page's existing look - it reuses the `nav-status` container the
"Testnet Live" pill already lives in, borrows the same font/colour variables, and adds no
new imagery, no framework, no layout reflow. Roughly 60 lines of vanilla JS, no build
step, no dependency (the explorer is a static bundle - adding a toolchain would be a
regression, and every new dependency is one more thing for Halborn to review).

Behaviour:
  * options are fetched from /api/v1/networks - the server's allow-list decides what the
    UI may offer, so the frontend cannot invent a network
  * an option whose `genesis_ok` is false renders disabled with the reason as a tooltip;
    the UI never displays data from an endpoint that failed genesis verification
  * the choice is kept in localStorage AND reflected in ?network= so a link is shareable
  * a visible banner states which chain the numbers came from - the failure mode this
    whole session has been fighting is data from one chain shown under another's name

The intentional "TESTNET - not mainnet, not investor-ready" disclaimer is NOT touched.
That is the project's positioning statement and is the user's call, not mine.
"""
import base64
import os
import subprocess
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
EXP = "/var/www/verdiscan/explorer/index.html"
TS = time.strftime("%Y%m%d-%H%M%S")


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


WIDGET = r"""
<!-- ===== network switcher (added during the site audit) =====
     Options come from the server's allow-list at /api/v1/networks; the frontend cannot
     invent a network. A network that fails genesis verification is shown disabled, so
     the UI never presents data from an unverified chain. Styling deliberately inherits
     the existing nav-status look - no new design, no new assets. -->
<style>
  .vnet-wrap{display:inline-flex;align-items:center;gap:.5rem;margin-right:.75rem;font:inherit}
  .vnet-sel{
    font:inherit;font-size:.8rem;padding:.25rem .5rem;border-radius:6px;
    border:1px solid rgba(0,0,0,.15);background:rgba(255,255,255,.9);
    color:inherit;cursor:pointer;line-height:1.4
  }
  .vnet-sel:disabled{opacity:.5;cursor:not-allowed}
  .vnet-note{
    font-size:.72rem;opacity:.75;white-space:nowrap
  }
  .vnet-warn{
    display:none;margin:0;padding:.5rem .75rem;font-size:.8rem;text-align:center;
    background:#fff4d6;color:#6b4b00;border-bottom:1px solid #f0d79a
  }
  .vnet-warn.show{display:block}
</style>
<div class="vnet-wrap" id="vnet-wrap" title="Chain shown by this explorer">
  <label for="vnet-select" class="vnet-note">Network</label>
  <select id="vnet-select" class="vnet-sel" aria-label="Select network"></select>
  <span class="vnet-note" id="vnet-status"></span>
</div>
<script>
(function(){
  // Same origin as the rest of the page's API calls.
  var API = (typeof window.API === 'string' && window.API) ? window.API : '/api';
  var sel = document.getElementById('vnet-select');
  var stat = document.getElementById('vnet-status');

  function currentChoice(){
    var q = new URLSearchParams(location.search).get('network');
    if (q) return q.toLowerCase();
    try { return (localStorage.getItem('verdis.network') || '').toLowerCase(); }
    catch(e){ return ''; }
  }

  function banner(msg, show){
    var b = document.getElementById('vnet-warn');
    if(!b){
      b = document.createElement('div');
      b.id = 'vnet-warn'; b.className = 'vnet-warn';
      document.body.insertBefore(b, document.body.firstChild);
    }
    b.textContent = msg || '';
    b.className = 'vnet-warn' + (show ? ' show' : '');
  }

  fetch(API + '/v1/networks', {cache:'no-store'})
    .then(function(r){ return r.json(); })
    .then(function(res){
      if(!res || !res.data){ throw new Error('bad payload'); }
      var want = currentChoice() || res.default;
      var chosen = null;
      res.data.forEach(function(n){
        var o = document.createElement('option');
        o.value = n.id;
        o.textContent = n.label + (n.enabled && n.genesis_ok ? '' : ' (unavailable)');
        if(!(n.enabled && n.genesis_ok)){
          o.disabled = true;
          o.title = n.problem || 'endpoint unavailable';
        }
        if(n.id === want && !o.disabled){ o.selected = true; chosen = n; }
        sel.appendChild(o);
      });
      // requested network unusable -> fall back to the server default, and SAY SO
      if(!chosen){
        var dflt = res.data.filter(function(n){ return n.id === res.default; })[0];
        if(dflt){
          sel.value = dflt.id; chosen = dflt;
          if(want && want !== res.default){
            banner('Network "' + want + '" is unavailable - showing ' + dflt.label + ' instead.', true);
          }
        }
      }
      if(chosen){
        var bits = [];
        if(chosen.best_block != null) bits.push('#' + chosen.best_block);
        if(chosen.peers != null) bits.push(chosen.peers + ' peers');
        stat.textContent = bits.join(' · ');
        // The point of the whole exercise: never show one chain's numbers under
        // another chain's name.
        if(chosen.id !== 'mainnet'){
          banner('Showing ' + chosen.label + ' data - not mainnet.', true);
        }
      }
    })
    .catch(function(e){
      sel.innerHTML = '<option>unavailable</option>';
      sel.disabled = true;
      stat.textContent = '';
      console.error('network list failed', e);
    });

  sel.addEventListener('change', function(){
    var v = sel.value;
    try { localStorage.setItem('verdis.network', v); } catch(e){}
    var u = new URL(location.href);
    u.searchParams.set('network', v);
    location.href = u.toString();
  });
})();
</script>
<!-- ===== end network switcher ===== -->
"""

print("=== target ===")
print(f"  {EXP}")
print(f"  nav-status present: {ssh(f'grep -c nav-status {EXP}')}")

if ssh(f"grep -c 'vnet-select' {EXP}") != "0":
    print("  switcher already present - refreshing it")
    ssh(f"cp {EXP} {EXP}.bak-switch-{TS}")
    # remove the previous block between the markers, then reinsert
    ssh(f"""python3 - <<'PY'
import re
p = "{EXP}"
s = open(p, encoding='utf-8', errors='ignore').read()
s = re.sub(r'<!-- ===== network switcher.*?<!-- ===== end network switcher ===== -->',
           '', s, flags=re.S)
open(p, 'w', encoding='utf-8').write(s)
print('  old block removed')
PY""")
else:
    ssh(f"cp {EXP} {EXP}.bak-switch-{TS}")
print(f"  backup: {EXP}.bak-switch-{TS}")

ssh(f"echo {base64.b64encode(WIDGET.encode()).decode()} | base64 -d > /tmp/vnet.html")

# insert inside the nav-status container so it sits with the existing pill
ins = ssh(f"""python3 - <<'PY'
p = "{EXP}"
w = open('/tmp/vnet.html', encoding='utf-8').read()
s = open(p, encoding='utf-8', errors='ignore').read()
key = '<div class="nav-status"'
i = s.find(key)
if i == -1:
    print('NAV_STATUS_NOT_FOUND')
else:
    j = s.find('>', i)
    s = s[:j+1] + w + s[j+1:]
    open(p, 'w', encoding='utf-8').write(s)
    print('INSERTED')
PY""")
print(f"  {ins}")

print("\n=== verify from the internet ===")
html = subprocess.run(["curl", "-s", "-m", "20", "https://explorer.verdischain.com"],
                      capture_output=True, text=True, timeout=60).stdout
for label, pat in (("switcher markup", "vnet-select"),
                   ("switcher script", "verdis.network"),
                   ("testnet disclaimer intact", "currently in testnet phase"),
                   ("logo reference intact", "verdis-logo-black.png")):
    print(f"  {label:<28} {'present' if pat in html else 'MISSING'}")
code = subprocess.run(["curl", "-s", "-o", os.devnull, "-w", "%{http_code}",
                       "-m", "20", "https://explorer.verdischain.com"],
                      capture_output=True, text=True, timeout=60).stdout
print(f"  page HTTP                    {code}")
