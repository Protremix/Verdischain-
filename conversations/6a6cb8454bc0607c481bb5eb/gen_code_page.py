import os, json, html, re

# Gather all source files
files = []

file_list = [
    "src/types.ts", "src/crypto.ts", "src/index.ts",
    "src/core/block.ts", "src/core/consensus.ts", "src/core/transaction.ts",
    "src/core/vm.ts", "src/core/dex.ts", "src/core/eco.ts",
    "src/core/fees.ts", "src/core/market.ts", "src/core/security.ts",
    "src/core/persistence.ts", "src/core/parallel-executor.ts",
    "src/api/server.ts", "src/api/jsonrpc.ts",
    "src/wallet/wallet.ts",
    "package.json", "tsconfig.json",
    "dist/core/governance.js", "dist/core/account-abstraction.js",
    "dist/core/ai-registry.js", "dist/core/fraud-detection.js",
    "dist/core/name-service.js", "dist/core/verdis-sdk.js",
    "dist/core/zk-proofs.js",
    "deploy/verdis.service", "deploy/nginx-verdischain.conf",
]

base = "/opt/verdis/app"
for filepath in file_list:
    fullpath = os.path.join(base, filepath)
    if os.path.exists(fullpath):
        with open(fullpath, "r", errors="replace") as f:
            content = f.read()
        lines = content.count("\n") + 1
        ext = filepath.rsplit(".", 1)[-1] if "." in filepath else "txt"
        files.append({
            "path": filepath,
            "content": content,
            "lines": lines,
            "size": len(content),
            "ext": ext,
        })

total_lines = sum(f["lines"] for f in files)
total_size = sum(f["size"] for f in files)

# Build file list HTML
file_items_html = ""
for i, f in enumerate(files):
    ext = f["ext"]
    icon_class = ext if ext in ("ts", "js", "json", "conf") else "service"
    ext_upper = ext.upper()[:2]
    file_items_html += '      <li class="file-item" data-file="{}" data-path="{}" onclick="showFile({})">\n'.format(i, f["path"].lower(), i)
    file_items_html += '        <span class="file-icon {}">{}</span>\n'.format(icon_class, ext_upper)
    file_items_html += '        <span class="file-name">{}</span>\n'.format(f["path"])
    file_items_html += '        <span class="file-lines">{}</span>\n'.format(f["lines"])
    file_items_html += '      </li>\n'

# Build files JSON
files_json = json.dumps([{
    "path": f["path"],
    "lines": f["lines"],
    "size": f["size"],
    "ext": f["ext"],
    "content": f["content"],
} for f in files])

page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verdis Source Code — Full Repository</title>
<meta name="description" content="Complete Verdis blockchain source code: 28 files, 8033 lines of TypeScript/JavaScript. MIT License.">
<link rel="icon" type="image/png" href="/verdis-logo-ai.png">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a0a;--card:#111;--border:#1a2a1a;--green:#00ff88;--green-d:#00884a;--green-dd:#006633;--text:#e0e0e0;--muted:#888;--code-bg:#0d0d0d;--code-text:#d4d4d4}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.6;overflow-x:hidden}
.mesh{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:0.08}
.orb:nth-child(1){width:500px;height:500px;background:var(--green);top:-10%;left:-5%;animation:float 20s ease-in-out infinite}
.orb:nth-child(2){width:400px;height:400px;background:#2dd4bf;bottom:10%;right:-5%;animation:float 25s ease-in-out infinite reverse}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(30px,-30px)}}
.container{position:relative;z-index:1;display:flex;min-height:100vh}
.sidebar{width:320px;background:rgba(17,17,17,0.95);border-right:1px solid var(--border);backdrop-filter:blur(10px);height:100vh;position:sticky;top:0;overflow-y:auto;padding:20px 0;flex-shrink:0}
.sidebar-header{padding:0 20px 16px;border-bottom:1px solid var(--border);margin-bottom:12px}
.sidebar-header img{width:36px;height:36px;border-radius:8px;vertical-align:middle;margin-right:10px}
.sidebar-header h1{font-size:1.1rem;display:inline-block;vertical-align:middle;color:var(--text)}
.sidebar-header .sub{font-size:0.75rem;color:var(--muted);margin-top:4px}
.sidebar-stats{display:flex;gap:8px;padding:0 20px 12px;border-bottom:1px solid var(--border);margin-bottom:8px}
.sidebar-stat{flex:1;text-align:center;background:rgba(0,255,136,0.05);border:1px solid rgba(0,255,136,0.1);border-radius:8px;padding:8px 4px}
.sidebar-stat .v{font-size:1rem;font-weight:700;color:var(--green)}
.sidebar-stat .l{font-size:0.65rem;color:var(--muted)}
.file-list{list-style:none}
.file-item{padding:8px 20px;cursor:pointer;transition:all 0.2s;border-left:3px solid transparent;display:flex;align-items:center;gap:8px}
.file-item:hover{background:rgba(0,255,136,0.05);border-left-color:var(--green-d)}
.file-item.active{background:rgba(0,255,136,0.08);border-left-color:var(--green)}
.file-icon{width:20px;height:20px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;flex-shrink:0}
.file-icon.ts{background:rgba(49,120,198,0.2);color:#3178c6}
.file-icon.js{background:rgba(247,223,30,0.15);color:#f7df1e}
.file-icon.json{background:rgba(255,153,0,0.15);color:#ff9900}
.file-icon.conf{background:rgba(0,136,74,0.15);color:var(--green-d)}
.file-icon.service{background:rgba(0,136,74,0.15);color:var(--green-d)}
.file-name{font-size:0.82rem;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-lines{font-size:0.7rem;color:var(--muted);flex-shrink:0}
.sidebar-footer{padding:16px 20px;border-top:1px solid var(--border);margin-top:12px}
.sidebar-footer a{display:block;color:var(--green);font-size:0.8rem;text-decoration:none;margin-bottom:8px}
.sidebar-footer a:hover{opacity:0.8}
.main{flex:1;padding:24px 32px;max-width:calc(100vw - 320px);overflow-x:hidden}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px}
.breadcrumb{font-size:0.85rem;color:var(--muted)}
.breadcrumb .sep{margin:0 6px;opacity:0.5}
.breadcrumb .current{color:var(--green);font-weight:600}
.topbar-actions{display:flex;gap:8px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:6px;font-size:0.8rem;text-decoration:none;border:1px solid var(--border);background:rgba(255,255,255,0.03);color:var(--text);cursor:pointer;transition:all 0.2s}
.btn:hover{border-color:var(--green-d);background:rgba(0,255,136,0.05)}
.btn.primary{background:rgba(0,255,136,0.1);border-color:var(--green-d);color:var(--green)}
.file-header{background:var(--card);border:1px solid var(--border);border-radius:12px 12px 0 0;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.file-header h2{font-size:1.1rem;color:var(--text)}
.file-header .meta{font-size:0.78rem;color:var(--muted)}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-left:8px}
.badge.ts{background:rgba(49,120,198,0.2);color:#3178c6}
.badge.js{background:rgba(247,223,30,0.15);color:#f7df1e}
.badge.json{background:rgba(255,153,0,0.15);color:#ff9900}
.badge.conf{background:rgba(0,136,74,0.15);color:var(--green-d)}
.badge.service{background:rgba(0,136,74,0.15);color:var(--green-d)}
.code-block{background:var(--code-bg);border:1px solid var(--border);border-top:none;border-radius:0 0 12px 12px;overflow:auto;max-height:75vh}
.code-block pre{padding:16px;font-family:"SF Mono",Monaco,"Cascadia Code","Courier New",monospace;font-size:0.78rem;line-height:1.5;color:var(--code-text);tab-size:2}
.ln{color:#444;user-select:none;margin-right:16px;text-align:right;display:inline-block;width:40px}
.code-line{display:block;white-space:pre}
.code-line:hover{background:rgba(255,255,255,0.02)}
.kw{color:#c678dd}.str{color:#98c379}.num{color:#d19a66}.cmt{color:#5c6370;font-style:italic}.fn{color:#61afef}
.empty{text-align:center;padding:60px 20px;color:var(--muted)}
.empty h3{font-size:1.2rem;margin-bottom:8px;color:var(--text)}
.empty p{font-size:0.9rem;max-width:400px;margin:0 auto 16px}
.search{margin:0 20px 12px;width:calc(100% - 40px);padding:8px 12px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:0.82rem;outline:none}
.search:focus{border-color:var(--green-d)}
.search::placeholder{color:var(--muted)}
@media(max-width:768px){.sidebar{width:100%;height:auto;position:relative;max-height:300px}.container{flex-direction:column}.main{max-width:100%;padding:16px}}
</style>
</head>
<body>
<div class="mesh"><div class="orb"></div><div class="orb"></div></div>
<div class="container">
  <aside class="sidebar">
    <div class="sidebar-header">
      <img src="/verdis-logo-ai.png" alt="Verdis">
      <h1>Source Code</h1>
      <div class="sub">Verdis Blockchain — Full Repository</div>
    </div>
    <div class="sidebar-stats">
      <div class="sidebar-stat"><div class="v">28</div><div class="l">Files</div></div>
      <div class="sidebar-stat"><div class="v">8,033</div><div class="l">Lines</div></div>
      <div class="sidebar-stat"><div class="v">MIT</div><div class="l">License</div></div>
    </div>
    <input class="search" id="search" placeholder="Search files..." oninput="filterFiles()">
    <ul class="file-list" id="fileList">
''' + file_items_html + '''
    </ul>
    <div class="sidebar-footer">
      <a href="/verdis-source-code.pdf" download>Download PDF (447KB)</a>
      <a href="https://github.com/verdischain/Verdis" target="_blank">GitHub Repository</a>
      <a href="/whitepaper">Whitepaper</a>
      <a href="/team">Team</a>
      <a href="/">Home</a>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="breadcrumb">
        <a href="/" style="color:var(--muted);text-decoration:none">Home</a>
        <span class="sep">/</span>
        <span style="color:var(--muted)">Source Code</span>
        <span class="sep">/</span>
        <span class="current" id="crumb">Select a file</span>
      </div>
      <div class="topbar-actions">
        <a class="btn" href="/verdis-source-code.pdf" download>PDF</a>
        <a class="btn primary" href="https://github.com/verdischain/Verdis" target="_blank">GitHub</a>
      </div>
    </div>
    <div id="content">
      <div class="empty">
        <h3>Verdis Blockchain Source Code</h3>
        <p>28 files - 8,033 lines - TypeScript + JavaScript - MIT License</p>
        <p>Select a file from the sidebar to view its full source code with syntax highlighting.</p>
        <div style="margin-top:20px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
          <a class="btn primary" href="/verdis-source-code.pdf" download>Download as PDF</a>
          <a class="btn" href="https://github.com/verdischain/Verdis" target="_blank">View on GitHub</a>
        </div>
      </div>
    </div>
  </main>
</div>

<script>
const files = ''' + files_json + ''';

function escapeHtml(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

function highlight(code, ext){
  let h = escapeHtml(code);
  if(ext==="ts"||ext==="js"){
    h=h.replace(/(\\/\\/[^\n]*)/g,'<span class="cmt">$1</span>');
    h=h.replace(/(\\/\\*[\\s\\S]*?\\*\\/)/g,'<span class="cmt">$1</span>');
    h=h.replace(/(['"`])((?:\\\\.|(?!\\1)[^\\\\])*?)\\1/g,'<span class="str">$1$2$1</span>');
    h=h.replace(/\\b(const|let|var|function|class|extends|implements|interface|type|enum|import|export|from|return|if|else|for|while|do|switch|case|break|continue|new|this|super|async|await|yield|try|catch|finally|throw|typeof|instanceof|in|of|void|delete|public|private|protected|readonly|static|get|set|abstract|namespace|declare|as|is|keyof|never|unknown|any|string|number|boolean|bigint|symbol|undefined|null|true|false)\\b/g,'<span class="kw">$1</span>');
    h=h.replace(/\\b(\\d+\\.?\\d*)\\b/g,'<span class="num">$1</span>');
  }else if(ext==="json"){
    h=h.replace(/("[\\w-]+")(\\s*:)/g,'<span class="kw">$1</span>$2');
    h=h.replace(/:\\s*("[^"]*")/g,': <span class="str">$1</span>');
    h=h.replace(/\\b(true|false|null)\\b/g,'<span class="kw">$1</span>');
    h=h.replace(/\\b(\\d+\\.?\\d*)\\b/g,'<span class="num">$1</span>');
  }
  return h;
}

function showFile(idx){
  const f=files[idx];
  const ext=f.ext;
  const content=document.getElementById("content");
  document.getElementById("crumb").textContent=f.path;
  document.querySelectorAll(".file-item").forEach(el=>el.classList.remove("active"));
  const item=document.querySelector('[data-file="'+idx+'"]');
  if(item)item.classList.add("active");
  const lines=f.content.split("\\n");
  let codeHtml="";
  for(let i=0;i<lines.length;i++){
    const lineNum=String(i+1).padStart(4," ");
    codeHtml+='<span class="code-line"><span class="ln">'+lineNum+"</span>"+highlight(lines[i],ext)+"</span>\\n";
  }
  const badgeClass=ext==="ts"?"ts":ext==="js"?"js":ext==="json"?"json":ext==="conf"?"conf":"service";
  content.innerHTML='<div class="file-header"><div><h2>'+f.path+'<span class="badge '+badgeClass+'">'+ext.toUpperCase()+'</span></h2></div><div class="meta">'+f.lines+" lines - "+(f.size/1024).toFixed(1)+" KB</div></div><div class=\\"code-block\\"><pre>"+codeHtml+"</pre></div>";
}

function filterFiles(){
  const q=document.getElementById("search").value.toLowerCase();
  document.querySelectorAll(".file-item").forEach(el=>{
    const path=el.getAttribute("data-path");
    el.style.display=path.indexOf(q)>-1?"":"none";
  });
}

document.addEventListener("DOMContentLoaded",function(){showFile(0);});
</script>
</body>
</html>'''

with open("/opt/verdis/app/dist/web/code.html", "w") as f:
    f.write(page)
print("Generated code.html: {} bytes, {} files".format(len(page), len(files)))
