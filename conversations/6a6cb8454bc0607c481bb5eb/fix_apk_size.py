with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()
content = content.replace("29.7MB", "28.3MB")
with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)
print("Fixed APK size to 28.3MB")
