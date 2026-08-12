#!/usr/bin/env python3
"""Fix faucet to show real API error messages instead of generic 'API error'."""

with open('/var/www/verdiscan/faucet/index.html', 'r') as f:
    content = f.read()

old = """    } else {
      throw new Error('API error');
    }
  } catch (e) {
    btn.textContent = 'Request Failed';
    btn.style.background = '#ef4444';
    alert('Faucet request failed: ' + (e.message || 'Network error') + '. Please try again.');"""

new = """    } else {
      let errMsg = 'API error';
      try {
        const errData = await res.json();
        errMsg = errData.error || errData.message || errMsg;
      } catch(e) {}
      throw new Error(errMsg);
    }
  } catch (e) {
    btn.textContent = 'Request Failed';
    btn.style.background = '#ef4444';
    alert('Faucet request failed: ' + (e.message || 'Network error'));"""

if old in content:
    content = content.replace(old, new, 1)
    with open('/var/www/verdiscan/faucet/index.html', 'w') as f:
        f.write(content)
    print("PATCHED: Real error messages now shown (e.g. rate limit countdown)")
else:
    print("NOT FOUND")
