with open("/var/www/verdiscan/explorer/index.html", "r") as f:
    content = f.read()

# Add a flag to track first load and prevent skeleton on subsequent loads
# Replace the skeleton line in loadLatestBlocks
old_skeleton = "tbody.innerHTML = '<tr><td colspan=\"4\"><span class=\"skel\" style=\"width:100%\"></span></td></tr>';"
new_skeleton = "if (!window._blocksLoaded) tbody.innerHTML = '<tr><td colspan=\"4\"><span class=\"skel\" style=\"width:100%\"></span></td></tr>';"

content = content.replace(old_skeleton, new_skeleton)

# Add _blocksLoaded flag after the tbody.innerHTML = html line
old_html_set = "tbody.innerHTML = html || '<tr><td colspan=\"4\" style=\"text-align:center;color:var(--text-3)\">No blocks</td></tr>';\n  \n  loadLatestExtrinsics();"
new_html_set = "tbody.innerHTML = html || '<tr><td colspan=\"4\" style=\"text-align:center;color:var(--text-3)\">No blocks</td></tr>';\n  window._blocksLoaded = true;\n  loadLatestExtrinsics();"

content = content.replace(old_html_set, new_html_set)

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Fixed - no more skeleton flicker on refresh!")
