#!/usr/bin/env python3
"""Fix the web wallet's broken recoverFromEmail function and subsequent code."""
import sys

path = '/var/www/verdiscan/wallet/index.html'

with open(path) as f:
    lines = f.readlines()

# Find the broken line
broken_idx = None
for i, line in enumerate(lines):
    if '// Verify it' in line and 'mnemonicconst' in line:
        broken_idx = i
        break

if broken_idx is None:
    print('ERROR: broken line not found')
    sys.exit(1)

print(f'Found broken line at index {broken_idx} (line {broken_idx + 1}), length {len(lines[broken_idx])} chars')

# Get prefix (everything before broken line)
prefix = lines[:broken_idx]

# Get the broken line content
content = lines[broken_idx].rstrip('\n')

# Find where the comment starts
comment_start = content.index('// Verify')
indent = content[:comment_start]

# Get suffix (everything after broken line)
suffix = lines[broken_idx + 1:]

# Check if the broken line included </script> - if so, suffix won't have it
# But we need to check if suffix has additional content
has_script_close = '</script>' in content
print(f'Broken line contains </script>: {has_script_close}')

# Build the fixed code
fixed_lines = []
fixed_lines.append(indent + "// Verify it's a valid 12-word mnemonic\n")
fixed_lines.append('    const words = mnemonic.trim().split(/\\s+/);\n')
fixed_lines.append('    if (words.length !== 12) {\n')
fixed_lines.append("      toast('Decryption failed \u2014 wrong password?', 'error');\n")
fixed_lines.append('      return;\n')
fixed_lines.append('    }\n')
fixed_lines.append('\n')
fixed_lines.append('    // Import the recovered wallet\n')
fixed_lines.append('    const { address, publicKey } = await deriveAddressFromMnemonic(mnemonic);\n')
fixed_lines.append('    saveWallet(mnemonic, publicKey, address);\n')
fixed_lines.append('    await unlockWallet(mnemonic);\n')
fixed_lines.append("    toast('Wallet recovered successfully!', 'success');\n")
fixed_lines.append('    setTimeout(loadDashboard, 500);\n')
fixed_lines.append('  } catch (e) {\n')
fixed_lines.append("    toast('Recovery failed: ' + e.message + ' (wrong password?)', 'error');\n")
fixed_lines.append('  }\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// ===== ANIMATED BALANCE COUNTER =====\n')
fixed_lines.append('function animateBalance(targetStr) {\n')
fixed_lines.append("  const el = document.getElementById('balanceDisplay');\n")
fixed_lines.append('  if (!el) return;\n')
fixed_lines.append('  // Parse target value\n')
fixed_lines.append('  const target = parseFloat(targetStr) || 0;\n')
fixed_lines.append("  const current = parseFloat(el.dataset.value || '0');\n")
fixed_lines.append('  el.dataset.value = target;\n')
fixed_lines.append('  // Flash the card\n')
fixed_lines.append("  const card = el.closest('.balance-card');\n")
fixed_lines.append('  if (card) {\n')
fixed_lines.append("    card.classList.remove('updating');\n")
fixed_lines.append('    void card.offsetWidth; // reflow\n')
fixed_lines.append("    card.classList.add('updating');\n")
fixed_lines.append('  }\n')
fixed_lines.append('  const duration = 800;\n')
fixed_lines.append('  const start = performance.now();\n')
fixed_lines.append('  const diff = target - current;\n')
fixed_lines.append('  function tick(now) {\n')
fixed_lines.append('    const elapsed = now - start;\n')
fixed_lines.append('    const progress = Math.min(elapsed / duration, 1);\n')
fixed_lines.append('    // Ease-out cubic\n')
fixed_lines.append('    const eased = 1 - Math.pow(1 - progress, 3);\n')
fixed_lines.append('    const value = current + diff * eased;\n')
fixed_lines.append('    // Format with 9 decimals\n')
fixed_lines.append("    el.innerHTML = value.toFixed(9) + '<span class=\"unit\">VRDX</span>';\n")
fixed_lines.append('    if (progress < 1) {\n')
fixed_lines.append('      requestAnimationFrame(tick);\n')
fixed_lines.append('    } else {\n')
fixed_lines.append("      el.innerHTML = targetStr + '<span class=\"unit\">VRDX</span>';\n")
fixed_lines.append('    }\n')
fixed_lines.append('  }\n')
fixed_lines.append('  requestAnimationFrame(tick);\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// ===== SKELETON LOADER HELPERS =====\n')
fixed_lines.append('function showSkeleton(elId, lines = 1) {\n')
fixed_lines.append("  const el = document.getElementById(elId);\n")
fixed_lines.append('  if (!el) return;\n')
fixed_lines.append("  let html = '';\n")
fixed_lines.append('  for (let i = 0; i < lines; i++) {\n')
fixed_lines.append("    html += '<div class=\"skeleton skeleton-line\" style=\"width:' + (60 + Math.random() * 35) + '%\"></div>';\n")
fixed_lines.append('  }\n')
fixed_lines.append('  el.innerHTML = html;\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('function showBalanceSkeleton() {\n')
fixed_lines.append("  const el = document.getElementById('balanceDisplay');\n")
fixed_lines.append('  if (!el) return;\n')
fixed_lines.append("  el.innerHTML = '<span class=\"skeleton\" style=\"display:inline-block;width:160px;height:22px\"></span>';\n")
fixed_lines.append("  const sub = document.getElementById('balanceSub');\n")
fixed_lines.append("  if (sub) sub.innerHTML = '<span class=\"skeleton\" style=\"display:inline-block;width:120px;height:14px\"></span>';\n")
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('function showAddressSkeleton() {\n')
fixed_lines.append("  const el = document.getElementById('dashAddress');\n")
fixed_lines.append('  if (!el) return;\n')
fixed_lines.append("  el.innerHTML = '<span class=\"skeleton\" style=\"display:inline-block;width:200px;height:16px\"></span>';\n")
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// ===== FLOATING PARTICLES IN HERO =====\n')
fixed_lines.append('function initParticles() {\n')
fixed_lines.append("  const hero = document.querySelector('.wallet-hero');\n")
fixed_lines.append('  if (!hero) return;\n')
fixed_lines.append('  for (let i = 0; i < 8; i++) {\n')
fixed_lines.append("    const p = document.createElement('div');\n")
fixed_lines.append("    p.className = 'particle';\n")
fixed_lines.append('    const size = 2 + Math.random() * 4;\n')
fixed_lines.append("    p.style.width = size + 'px';\n")
fixed_lines.append("    p.style.height = size + 'px';\n")
fixed_lines.append("    p.style.background = 'rgba(132,254,135,' + (0.2 + Math.random() * 0.3) + ')';\n")
fixed_lines.append("    p.style.left = (Math.random() * 100) + '%';\n")
fixed_lines.append("    p.style.bottom = '0';\n")
fixed_lines.append("    p.style.animationDuration = (4 + Math.random() * 6) + 's';\n")
fixed_lines.append("    p.style.animationDelay = (Math.random() * 5) + 's';\n")
fixed_lines.append('    hero.appendChild(p);\n')
fixed_lines.append('  }\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// ===== COPY FEEDBACK =====\n')
fixed_lines.append('const _originalCopy = window.copyToClipboard;\n')
fixed_lines.append('if (_originalCopy) {\n')
fixed_lines.append('  window.copyToClipboard = function(text) {\n')
fixed_lines.append('    navigator.clipboard.writeText(text).then(() => {\n')
fixed_lines.append("      toast('Copied to clipboard', 'success');\n")
fixed_lines.append('      // Flash the address element if copying address\n')
fixed_lines.append("      const addrEl = document.getElementById('dashAddress');\n")
fixed_lines.append('      if (addrEl && addrEl.textContent === text) {\n')
fixed_lines.append("        addrEl.classList.remove('copied');\n")
fixed_lines.append('        void addrEl.offsetWidth;\n')
fixed_lines.append("        addrEl.classList.add('copied');\n")
fixed_lines.append('      }\n')
fixed_lines.append('    });\n')
fixed_lines.append('  };\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// ===== LOADING SPINNER FOR BUTTONS =====\n')
fixed_lines.append('function showBtnSpinner(btnId) {\n')
fixed_lines.append("  const btn = document.getElementById(btnId);\n")
fixed_lines.append('  if (!btn) return;\n')
fixed_lines.append('  btn.dataset.originalText = btn.innerHTML;\n')
fixed_lines.append('  btn.disabled = true;\n')
fixed_lines.append("  btn.innerHTML = '<span class=\"spinner\"></span> Processing...';\n")
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('function hideBtnSpinner(btnId) {\n')
fixed_lines.append("  const btn = document.getElementById(btnId);\n")
fixed_lines.append('  if (!btn) return;\n')
fixed_lines.append('  btn.disabled = false;\n')
fixed_lines.append('  if (btn.dataset.originalText) btn.innerHTML = btn.dataset.originalText;\n')
fixed_lines.append('}\n')
fixed_lines.append('\n')
fixed_lines.append('// Init particles on page load\n')
fixed_lines.append("window.addEventListener('load', () => {\n")
fixed_lines.append('  setTimeout(initParticles, 200);\n')
fixed_lines.append('});\n')
fixed_lines.append('</script>\n')

# Skip suffix if it starts with </script> (which we already included)
if suffix and '</script>' in suffix[0]:
    # Check if there's more after </script>
    after_script = suffix[0][suffix[0].index('</script>') + len('</script>'):]
    suffix = suffix[1:]
    if after_script.strip():
        suffix = [after_script] + suffix

with open(path, 'w') as f:
    f.writelines(prefix)
    f.writelines(fixed_lines)
    f.writelines(suffix)

print(f'Fixed: replaced broken line {broken_idx + 1} with {len(fixed_lines)} properly formatted lines')
