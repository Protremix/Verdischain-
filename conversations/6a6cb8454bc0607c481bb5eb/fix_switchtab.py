import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# Fix switchTab to add holders case
old_switch = '''  if (t==='topaccounts') loadTopAccounts();
}'''

new_switch = '''  if (t==='topaccounts') loadTopAccounts();
  if (t==='holders') loadHolders();
}'''

if old_switch in content:
    content = content.replace(old_switch, new_switch)
    print("Fixed switchTab to call loadHolders")
else:
    print("ERROR: switchTab pattern not found")

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
