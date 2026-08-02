import re

with open("/opt/verdis/app/dist/web/token-sale.html", "r") as f:
    content = f.read()

# Fix 1: Replace tokReviewConsent - make button always clickable, visual feedback only
idx = content.find("window.tokReviewConsent")
if idx >= 0:
    start = content.rfind("<script>", 0, idx)
    end = content.find("</script>", idx) + 9
    old_block = content[start:end]
    
    new_script = """<script>
if(typeof tokReviewConsent !== "function"){
  window.tokReviewConsent = function(cb){
    document.querySelectorAll(".tok-buy-btn").forEach(function(b){
      if(cb.checked){
        b.style.opacity = "1";
        b.style.pointerEvents = "auto";
        b.title = "";
      } else {
        b.style.opacity = "0.7";
        b.style.pointerEvents = "auto";
        b.title = "Review tokenomics and check the box to confirm";
      }
    });
  };
  document.addEventListener("DOMContentLoaded", function(){
    document.querySelectorAll(".tok-buy-btn").forEach(function(b){
      b.style.opacity = "0.85";
      b.style.pointerEvents = "auto";
    });
  });
}
</script>"""
    content = content.replace(old_block, new_script)
    print("Fixed tokReviewConsent block")
else:
    print("ERROR: tokReviewConsent not found")

# Fix 2: Replace the hard consent gate in executePurchase
old_gate_start = "      // Consent gate - block purchase if disclosure not accepted"
old_gate_end = "        return;\n      }\n\n      // Call the real IDO API"
new_gate = """      // Consent gate - friendly scroll+highlight if not checked
      const consentBox = document.getElementById("tokReviewCheck");
      if (!consentBox || !consentBox.checked) {
        if (consentBox) {
          consentBox.scrollIntoView({ behavior: "smooth", block: "center" });
          const wrap = consentBox.parentElement;
          if (wrap) { wrap.style.outline = "2px solid #ff4444"; setTimeout(function(){ wrap.style.outline = ""; }, 3000); }
        }
        const banner = document.createElement("div");
        banner.style.cssText = "position:fixed;top:24px;left:50%;transform:translateX(-50%);background:#ff4444;color:#fff;padding:14px 28px;border-radius:10px;z-index:9999;font-weight:bold;font-size:14px;box-shadow:0 4px 20px rgba(255,68,68,0.5);";
        banner.textContent = "Please check the tokenomics consent box before purchasing.";
        document.body.appendChild(banner);
        setTimeout(function(){ banner.remove(); }, 4000);
        return;
      }

      // Call the real IDO API"""

# Find and replace the consent gate
gate_start_idx = content.find(old_gate_start)
if gate_start_idx >= 0:
    gate_end_idx = content.find("      // Call the real IDO API", gate_start_idx)
    if gate_end_idx >= 0:
        old_gate = content[gate_start_idx:gate_end_idx]
        content = content[:gate_start_idx] + new_gate
        content = content + ""  # we need to put back the rest
        # Actually rebuild properly
        pass
    print(f"Found gate at {gate_start_idx}")
else:
    print("Gate not found")

# Redo: simpler approach - find the block and replace it
with open("/opt/verdis/app/dist/web/token-sale.html", "r") as f:
    content = f.read()

# Fix 1 again cleanly
idx = content.find("window.tokReviewConsent")
if idx >= 0:
    start = content.rfind("<script>", 0, idx)
    end = content.find("</script>", idx) + 9
    old_block = content[start:end]
    
    new_script = '<script>\nif(typeof tokReviewConsent !== "function"){\n  window.tokReviewConsent = function(cb){\n    document.querySelectorAll(".tok-buy-btn").forEach(function(b){\n      b.style.opacity = cb.checked ? "1" : "0.75";\n      b.style.pointerEvents = "auto";\n    });\n  };\n  document.addEventListener("DOMContentLoaded", function(){\n    document.querySelectorAll(".tok-buy-btn").forEach(function(b){\n      b.style.opacity = "0.85";\n      b.style.pointerEvents = "auto";\n    });\n  });\n}\n</script>'
    
    content = content.replace(old_block, new_script)
    print("Fix 1 done: tokReviewConsent always enables pointer-events")

# Fix 2: consent gate
gate_marker = "// Consent gate - block purchase if disclosure not accepted"
gate_idx = content.find(gate_marker)
if gate_idx >= 0:
    # Find the end of the if block: "        return;\n      }"
    end_marker = "        return;\n      }\n"
    end_idx = content.find(end_marker, gate_idx)
    if end_idx >= 0:
        end_pos = end_idx + len(end_marker)
        new_gate_block = '      // Consent gate - scroll to checkbox if unchecked\n      if (!document.getElementById("tokReviewCheck") || !document.getElementById("tokReviewCheck").checked) {\n        const cb = document.getElementById("tokReviewCheck");\n        if (cb) { cb.scrollIntoView({behavior:"smooth",block:"center"}); cb.parentElement.style.outline="2px solid #ff4444"; setTimeout(function(){cb.parentElement.style.outline="";},3000); }\n        const b = document.createElement("div"); b.style.cssText="position:fixed;top:24px;left:50%;transform:translateX(-50%);background:#ff4444;color:#fff;padding:14px 28px;border-radius:10px;z-index:9999;font-weight:bold;font-size:14px;"; b.textContent="Please check the tokenomics consent box first."; document.body.appendChild(b); setTimeout(function(){b.remove();},4000);\n        return;\n      }\n'
        content = content[:gate_idx] + new_gate_block + content[end_pos:]
        print("Fix 2 done: friendly consent gate with scroll+banner")
    else:
        print("ERROR: Could not find end of consent gate block")
else:
    print("ERROR: Consent gate marker not found")

# Fix 3: use selectedAsset not hardcoded USDT
old_usdt = 'asset: \'USDT\','
new_asset_line = 'asset: selectedAsset,'
if old_usdt in content:
    content = content.replace(old_usdt, new_asset_line)
    print("Fix 3 done: use selectedAsset")
else:
    print("Fix 3: USDT not found, checking...")
    # Try double quotes
    old_usdt2 = 'asset: "USDT",'
    if old_usdt2 in content:
        content = content.replace(old_usdt2, new_asset_line)
        print("Fix 3 done (double quotes)")

with open("/opt/verdis/app/dist/web/token-sale.html", "w") as f:
    f.write(content)
print("\nAll fixes saved to token-sale.html")
