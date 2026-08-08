with open("page2_script.js", "r") as f:
    code = f.read()

# Let's print code after the endpoints array
idx = code.find("function renderSidebar")
if idx != -1:
    print(code[idx:])
else:
    print(code[:2000])
