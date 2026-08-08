import urllib.request
import json

def call_rpc(method, params=[]):
    url = 'https://verdischain.com/rpc'
    data = json.dumps({'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        res = urllib.request.urlopen(req)
        body = res.read().decode('utf-8')
        return json.loads(body)
    except Exception as e:
        return {'error': str(e)}

print("chain_getHeader:", call_rpc("chain_getHeader"))
print("system_health:", call_rpc("system_health"))
print("dpos_activeValidators:", call_rpc("dpos_activeValidators"))
print("dpos_allValidators:", call_rpc("dpos_allValidators"))
