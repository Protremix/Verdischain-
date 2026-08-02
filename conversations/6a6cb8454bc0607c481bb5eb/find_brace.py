import re, subprocess

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
main_script = scripts[1]
lines = main_script.split("\n")

# Check if adding one } at the end fixes it
with open("/tmp/extra_brace.js", "w") as f:
    f.write(main_script + "\n}\n")
result = subprocess.run(["node", "--check", "/tmp/extra_brace.js"], capture_output=True, text=True, timeout=5)
print(f"Full script + extra }}: {'OK' if result.returncode == 0 else result.stderr[:200]}")

# Find where the break is by checking progressive chunks
for n in [500, 700, 800, 900, 1000, 1050, 1070, 1080, 1090, 1100, 1110, 1115]:
    chunk = "\n".join(lines[:n]) + "\n}"
    with open("/tmp/chunk_check.js", "w") as f:
        f.write(chunk)
    result = subprocess.run(["node", "--check", "/tmp/chunk_check.js"], capture_output=True, text=True, timeout=5)
    status = "OK" if result.returncode == 0 else "ERR"
    print(f"Lines 1-{n} + }}: {status}")
    if result.stderr and status == "ERR" and n >= 1000:
        print(f"  {result.stderr[:150]}")
