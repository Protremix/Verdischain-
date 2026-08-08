import re

with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()

# Fix 1: Replace the success check to use result.ok instead of result.success
old_check = """    if (result && result.success) {
      toast(`Transaction submitted! Hash: ${result.data?.hash?.slice(0, 16) || 'pending'}...`, 'success');
    } else {
      // Try author_submitExtrinsic via RPC (for raw extrinsic submission)
      toast(`Transaction signed (sig: ${sigHex.slice(0, 20)}...) — broadcast to network`, 'success');
      console.log('Transaction signed:', { payload, signature: sigHex });
    }"""

new_check = """    if (result && result.ok) {
      toast(`Transaction on-chain! Hash: ${result.extrinsic_hash?.slice(0, 20) || 'pending'}...`, 'success');
      console.log('TX Relay result:', result);
    } else if (result && result.error) {
      toast('Relay error: ' + result.error, 'error');
    } else {
      toast('Transaction signed (sig: ' + sigHex.slice(0, 20) + '...) — broadcast to network', 'success');
      console.log('Transaction signed:', { payload, signature: sigHex });
    }"""

if old_check in content:
    content = content.replace(old_check, new_check)
    print("Fixed: ok check replaced")
else:
    print("WARNING: old_check not found, trying regex")
    pattern = r'if \(result && result\.success\).*?console\.log\(\'Transaction signed:\', \{ payload, signature: sigHex \}\);'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_check + content[match.end():]
        print("Fixed: ok check replaced via regex")
    else:
        print("ERROR: Could not find success check block")

# Fix 2: Toast function - add show class
old_toast = """function toast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 4000);
}"""

new_toast = """function toast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = 'toast ' + type + ' show';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 4000);
}"""

if old_toast in content:
    content = content.replace(old_toast, new_toast)
    print("Fixed: toast show class added")
else:
    print("WARNING: toast function not found exactly, trying regex")
    pattern = r"function toast\(msg, type = 'info'\).*?setTimeout\(\(\) => \{ t\.style\.opacity.*?t\.remove\(\)\}, 300\); \}, 4000\);"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_toast + content[match.end():]
        print("Fixed: toast replaced via regex")
    else:
        print("ERROR: Could not find toast function")

# Check toast CSS exists
if '.toast' in content:
    print("Toast CSS: present")
else:
    print("Toast CSS: MISSING - adding")
    toast_css = "\n.toast{position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:10px;font-size:13px;font-weight:600;z-index:10001;opacity:0;transform:translateY(10px);transition:all 300ms ease-out;max-width:400px}\n.toast.show{opacity:1;transform:translateY(0)}\n.toast.success{background:#16a34a;color:#fff}\n.toast.error{background:#dc2626;color:#fff}\n.toast.info{background:#0f172a;color:#fff}\n"
    content = content.replace('</style>', toast_css + '</style>')

with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)

print("Done. File size:", len(content))
print("result.ok present:", "result.ok" in content)
print("extrinsic_hash present:", "extrinsic_hash" in content)
