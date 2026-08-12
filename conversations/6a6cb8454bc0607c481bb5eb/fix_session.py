import re

with open('index.html', 'r') as f:
    content = f.read()

# 1. Add sessionStorage save in enterWallet (after saveWalletWithPin)
old_enter = """      toast('Wallet secured with PIN. It will persist across refreshes.', 'success');
    } catch (e) {
      toast('PIN encryption failed: ' + e.message, 'error');
      return;
    }
  }
  loadDashboard();
}"""

new_enter = """      toast('Wallet secured with PIN. It will persist across refreshes.', 'success');
      // Save session for auto-unlock on refresh
      if (_sessionMnemonic) {
        sessionStorage.setItem('verdis_session_mnemonic', _sessionMnemonic);
      }
    } catch (e) {
      toast('PIN encryption failed: ' + e.message, 'error');
      return;
    }
  }
  loadDashboard();
}"""

content = content.replace(old_enter, new_enter)

# 2. Find importWallet function and add sessionStorage save
match = re.search(r'async function importWallet\(\).*?(?=\n\n)', content, re.DOTALL)
if match:
    import_func = match.group(0)
    print('Found importWallet, length:', len(import_func))
    if 'sessionStorage' not in import_func:
        if "toast('Wallet imported" in import_func:
            import_func_new = import_func.replace(
                "toast('Wallet imported",
                "if (_sessionMnemonic) { sessionStorage.setItem('verdis_session_mnemonic', _sessionMnemonic); }\n      toast('Wallet imported"
            )
            content = content.replace(import_func, import_func_new)
            print('importWallet updated')
    else:
        print('importWallet already has sessionStorage')

# 3. Also handle recoverFromEmail
match2 = re.search(r'async function recoverFromEmail\(\).*?(?=\n\n)', content, re.DOTALL)
if match2:
    recover_func = match2.group(0)
    if 'sessionStorage' not in recover_func:
        if "toast('Wallet recovered" in recover_func:
            recover_new = recover_func.replace(
                "toast('Wallet recovered",
                "if (_sessionMnemonic) { sessionStorage.setItem('verdis_session_mnemonic', _sessionMnemonic); }\n      toast('Wallet recovered"
            )
            content = content.replace(recover_func, recover_new)
            print('recoverFromEmail updated')

with open('index.html', 'w') as f:
    f.write(content)

print('All session saves added')
