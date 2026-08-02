import re

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

# Find the stage progression section
idx = content.find("// Render stage progression")
if idx == -1:
    print("ERROR: Could not find stage progression marker")
    exit(1)

# Find the updateSaleUI() call after the stages block
end_idx = content.find("updateSaleUI();", idx)
if end_idx == -1:
    print("ERROR: Could not find updateSaleUI call")
    exit(1)

old_section = content[idx:end_idx]
print(f"Found section: {len(old_section)} chars")

# New section: update stage text FIRST, then try to render bar in isolated try-catch
new_section = """// Update stage info FIRST (before bar rendering which may fail)
      if(d.stages){
        const cs=document.getElementById('idoCurrentStage');
        if(cs) cs.textContent=d.phase+' (+'+d.bonusPct+'% bonus)';
        const sp=document.getElementById('idoStagePrice');
        if(sp) sp.textContent='$'+d.priceUSD+'/VRDX';
        const sb=document.getElementById('idoStageBonus');
        if(sb) sb.textContent='(+'+d.bonusPct+'% bonus tokens)';
        const mc=document.getElementById('idoMinContrib');
        if(mc) mc.textContent='$'+(d.minContribution||50);
        const mw=document.getElementById('idoMaxWallet');
        if(mw) mw.textContent='$'+((d.maxPerWallet||100000)/1000)+'k';
        // Render stage progression bar (isolated)
        try {
          const bar=document.getElementById('idoStagesBar');
          if(bar && Array.isArray(d.stages)) bar.innerHTML = d.stages.map(function(s){
            var active=s.isCurrent;
            var done=s.status==='completed';
            var pct=s.progressPct||'0.00';
            var bg=active?'rgba(0,255,136,0.15)':done?'rgba(0,255,136,0.05)':'rgba(255,255,255,0.03)';
            var border=active?'1px solid rgba(0,255,136,0.4)':'1px solid rgba(255,255,255,0.08)';
            var color=active?'#00ff88':done?'#00aa55':'#666';
            return '<div style="flex:1;min-width:140px;padding:12px;border-radius:8px;background:'+bg+';border:'+border+';text-align:center">'+
              '<div style="font-size:11px;color:#666;text-transform:uppercase">'+s.status+(active?' <':'')+'</div>'+
              '<div style="font-size:14px;font-weight:700;color:'+color+';margin:4px 0">'+s.name+'</div>'+
              '<div style="font-size:12px;color:#888">$'+s.price+'/VRDX</div>'+
              '<div style="font-size:11px;color:#aaa;margin-top:4px">+'+s.bonus+'% bonus</div>'+
              '<div style="margin-top:8px;height:4px;background:#222;border-radius:2px;overflow:hidden">'+
              '<div style="height:100%;width:'+pct+'%;background:'+color+';transition:width 0.5s"></div></div>'+
              '<div style="font-size:10px;color:#555;margin-top:4px">'+pct+'% sold</div></div>';
          }).join('');
        } catch(barErr) { console.warn('Stage bar render failed:', barErr); }
      }
      """

content = content[:idx] + new_section + content[end_idx:]
print("Section replaced successfully")

# Check for VRS references
vrs_matches = [(m.start(), content[max(0,m.start()-20):m.end()+20]) for m in re.finditer(r"\bVRS\b", content)]
print(f"VRS matches found: {len(vrs_matches)}")
for pos, ctx in vrs_matches[:15]:
    print(f"  @{pos}: ...{ctx}...")

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(content)
print("Dashboard saved")
