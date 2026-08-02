import re
import subprocess

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

# Remove diagnostic box and script
content = re.sub(r'<div id="diagBox".*?</script>', '', content, flags=re.DOTALL)

# Find init(); in the main script and add missing } after it
idx = content.rfind("init();")
if idx > 0:
    # Find the position right after init();
    insert_pos = idx + len("init();")
    content = content[:insert_pos] + "\n}" + content[insert_pos:]
    print("Added missing } after init()")
else:
    print("Could not find init()")

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(content)

# Verify the main script block
scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
for script in scripts:
    if "API_BASE" in script:
        with open("/tmp/verify_script.js", "w") as f:
            f.write(script)
        break

result = subprocess.run(["node", "--check", "/tmp/verify_script.js"], capture_output=True, text=True)
if result.returncode == 0:
    print("SYNTAX CHECK: PASSED")
else:
    print("SYNTAX CHECK: FAILED - " + result.stderr)

print("Dashboard saved")
