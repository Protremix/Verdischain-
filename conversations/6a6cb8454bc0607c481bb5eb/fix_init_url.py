path = '/opt/verdis/app/dist/web/dashboard.html'
with open(path) as f:
    html = f.read()

# Add URL param check before init() call at the end
init_call = "\ninit();\n"
url_check = """
// Check URL params for shared tx/block links
var urlParams=new URLSearchParams(location.search);
if(urlParams.get('tx')){setTimeout(function(){showTxDetail(urlParams.get('tx'))},1000)}
if(urlParams.get('block')){setTimeout(function(){showBlockDetail(parseInt(urlParams.get('block')))},1000)}
"""

if init_call in html:
    html = html.replace(init_call, url_check + init_call, 1)
    with open(path, 'w') as f:
        f.write(html)
    print('URL param check added before init() call')
else:
    print('ERROR: init() call not found')
