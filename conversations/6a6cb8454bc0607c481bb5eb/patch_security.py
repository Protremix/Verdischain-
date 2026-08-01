#!/usr/bin/env python3
"""Patch wallet.html to add PIN + biometric security layer."""
import re

with open("/opt/verdis/app/dist/web/wallet.html", "r", errors="replace") as f:
    html = f.read()

# ═══ 1. Add security CSS (before </style>) ═══
SECURITY_CSS = """
/* ═══ Security / Lock Screen ═══ */
.lock-screen {
    position: fixed; inset: 0; z-index: 300;
    background: var(--bg-dark); display: flex; flex-direction: column;
    align-items: center; justify-content: center; padding: 24px;
    animation: fadeIn 0.3s ease;
}
.lock-screen.hidden { display: none; }
.lock-logo svg { width: 72px; height: 72px; animation: logoGlow 3s ease-in-out infinite; margin-bottom: 20px; }
.lock-title { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.lock-subtitle { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 28px; text-align: center; }

/* PIN Dots */
.pin-display { display: flex; gap: 14px; margin-bottom: 28px; height: 16px; }
.pin-dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--border-color); transition: var(--transition); }
.pin-dot.filled { background: var(--accent-green); border-color: var(--accent-green); box-shadow: 0 0 8px rgba(0,255,136,0.4); }

/* PIN Keypad */
.pin-keypad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; width: 260px; }
.pin-key {
    height: 56px; border-radius: 16px; border: 1px solid var(--border-color);
    background: var(--bg-card); color: var(--text-primary); font-size: 1.4rem; font-weight: 600;
    cursor: pointer; transition: var(--transition); font-family: var(--font-main);
    display: flex; align-items: center; justify-content: center;
}
.pin-key:hover { border-color: var(--accent-green); color: var(--accent-green); background: rgba(0,255,136,0.05); }
.pin-key:active { transform: scale(0.95); background: rgba(0,255,136,0.1); }
.pin-key.action { font-size: 0.82rem; color: var(--text-muted); }
.pin-key.action:hover { color: var(--accent-red); border-color: var(--accent-red); }
.pin-key.fingerprint { background: rgba(0,255,136,0.05); border-color: rgba(0,255,136,0.2); }
.pin-key.fingerprint svg { width: 28px; height: 28px; color: var(--accent-green); }

/* Shake animation for wrong PIN */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-8px); }
    75% { transform: translateX(8px); }
}
.shake { animation: shake 0.3s ease; }

/* Lock error message */
.lock-error {
    font-size: 0.82rem; color: var(--accent-red); margin-top: 16px;
    opacity: 0; transition: opacity 0.3s; text-align: center;
}
.lock-error.show { opacity: 1; }

/* Security badge on header */
.security-badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px;
    border-radius: 100px; font-size: 0.62rem; font-weight: 600;
    background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.2); color: var(--accent-green);
    margin-left: 6px;
}
.security-badge svg { width: 10px; height: 10px; }

/* Setup screen */
.setup-screen { width: 100%; max-width: 340px; text-align: center; }
.setup-option {
    display: flex; align-items: center; gap: 14px; padding: 16px; border-radius: var(--radius-sm);
    background: var(--bg-card); border: 1px solid var(--border-color); margin-bottom: 10px;
    cursor: pointer; transition: var(--transition); text-align: left;
}
.setup-option:hover { border-color: var(--accent-green); background: rgba(0,255,136,0.03); }
.setup-option-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.setup-option-icon svg { width: 20px; height: 20px; }
.setup-option-text { flex: 1; }
.setup-option-title { font-weight: 600; font-size: 0.88rem; }
.setup-option-desc { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; }
.setup-option-check { width: 20px; height: 20px; border-radius: 50%; border: 2px solid var(--border-color); flex-shrink: 0; transition: var(--transition); }
.setup-option-check.checked { border-color: var(--accent-green); background: var(--accent-green); display: flex; align-items: center; justify-content: center; }
.setup-option-check.checked::after { content: '\\2713'; color: #03140c; font-size: 0.72rem; font-weight: 700; }

/* Auto-lock indicator */
.auto-lock-bar {
    position: fixed; top: 0; left: 0; height: 2px; background: var(--accent-green);
    z-index: 99; transition: width 0.1s linear; opacity: 0.5;
}
"""

html = html.replace("</style>", SECURITY_CSS + "\n</style>", 1)

# ═══ 2. Add lock screen HTML (right after <body> opening) ═══
LOCK_SCREEN = """
<!-- ═══ Lock Screen ═══ -->
<div class="lock-screen hidden" id="lockScreen">
    <div class="lock-logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
            <defs>
                <linearGradient id="lslg1" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stop-color="#00aa55"/><stop offset="50%" stop-color="#00ff88"/><stop offset="100%" stop-color="#66ffbb"/>
                </linearGradient>
                <linearGradient id="lslg2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00ff88"/><stop offset="100%" stop-color="#2dd4bf"/>
                </linearGradient>
                <filter id="lsgf"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
            <polygon points="100,18 168,58 168,142 100,182 32,142 32,58" fill="none" stroke="url(#lslg2)" stroke-width="2.5" opacity="0.5"/>
            <polygon points="100,28 160,65 160,135 100,172 40,135 40,65" fill="none" stroke="url(#lslg2)" stroke-width="3" filter="url(#lsgf)"/>
            <path d="M100,60 C100,60 75,80 72,105 C69,130 85,148 100,152 C115,148 131,130 128,105 C125,80 100,60 100,60 Z" fill="url(#lslg1)" opacity="0.9"/>
            <line x1="100" y1="60" x2="100" y2="152" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>
            <line x1="100" y1="105" x2="130" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>
            <line x1="100" y1="105" x2="70" y2="85" stroke="#00ff88" stroke-width="1" opacity="0.4"/>
        </svg>
    </div>
    <div class="lock-title" id="lockTitle">Enter PIN</div>
    <div class="lock-subtitle" id="lockSubtitle">Enter your 6-digit PIN to unlock</div>
    <div class="pin-display" id="pinDisplay">
        <div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div>
        <div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div>
    </div>
    <div class="pin-keypad" id="pinKeypad">
        <button class="pin-key" onclick="pinPress(1)">1</button>
        <button class="pin-key" onclick="pinPress(2)">2</button>
        <button class="pin-key" onclick="pinPress(3)">3</button>
        <button class="pin-key" onclick="pinPress(4)">4</button>
        <button class="pin-key" onclick="pinPress(5)">5</button>
        <button class="pin-key" onclick="pinPress(6)">6</button>
        <button class="pin-key" onclick="pinPress(7)">7</button>
        <button class="pin-key" onclick="pinPress(8)">8</button>
        <button class="pin-key" onclick="pinPress(9)">9</button>
        <button class="pin-key action" onclick="pinClear()">Clear</button>
        <button class="pin-key" onclick="pinPress(0)">0</button>
        <button class="pin-key fingerprint" id="biometricBtn" onclick="unlockBiometric()" style="display:none;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 11v2M9 11v3M15 11v3M6 11v4M18 11v4M3 13c0-4 2-7 9-7s9 3 9 7M3 15c0 3 2 5 9 5s9-2 9-5"/></svg>
        </button>
    </div>
    <div class="lock-error" id="lockError">Incorrect PIN. Try again.</div>
</div>

<!-- ═══ Security Setup Screen ═══ -->
<div class="lock-screen hidden" id="setupScreen">
    <div class="lock-logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
            <defs>
                <linearGradient id="sslg1" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stop-color="#00aa55"/><stop offset="50%" stop-color="#00ff88"/><stop offset="100%" stop-color="#66ffbb"/>
                </linearGradient>
                <linearGradient id="sslg2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00ff88"/><stop offset="100%" stop-color="#2dd4bf"/>
                </linearGradient>
                <filter id="ssgf"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
            <polygon points="100,18 168,58 168,142 100,182 32,142 32,58" fill="none" stroke="url(#sslg2)" stroke-width="2.5" opacity="0.5"/>
            <polygon points="100,28 160,65 160,135 100,172 40,135 40,65" fill="none" stroke="url(#sslg2)" stroke-width="3" filter="url(#ssgf)"/>
            <path d="M100,60 C100,60 75,80 72,105 C69,130 85,148 100,152 C115,148 131,130 128,105 C125,80 100,60 100,60 Z" fill="url(#lslg1)" opacity="0.9"/>
            <line x1="100" y1="60" x2="100" y2="152" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>
        </svg>
    </div>
    <div class="lock-title">Secure Your Wallet</div>
    <div class="lock-subtitle">Choose how to protect your Verdis wallet</div>
    <div class="setup-screen">
        <div class="setup-option" onclick="startPinSetup()">
            <div class="setup-option-icon" style="background:rgba(0,255,136,0.1);">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </div>
            <div class="setup-option-text">
                <div class="setup-option-title">PIN Code (Required)</div>
                <div class="setup-option-desc">6-digit numeric PIN</div>
            </div>
            <div class="setup-option-check" id="pinSetupCheck"></div>
        </div>
        <div class="setup-option" id="biometricSetupOption" onclick="toggleBiometricSetup()" style="display:none;">
            <div class="setup-option-icon" style="background:rgba(45,212,191,0.1);">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-teal)" stroke-width="2"><path d="M12 11v2M9 11v3M15 11v3M6 11v4M18 11v4M3 13c0-4 2-7 9-7s9 3 9 7M3 15c0 3 2 5 9 5s9-2 9-5"/></svg>
            </div>
            <div class="setup-option-text">
                <div class="setup-option-title">Biometric Unlock</div>
                <div class="setup-option-desc">Fingerprint / Face ID</div>
            </div>
            <div class="setup-option-check" id="biometricSetupCheck"></div>
        </div>
        <div class="setup-option" onclick="toggleAutoLock()">
            <div class="setup-option-icon" style="background:rgba(245,158,11,0.1);">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-orange)" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div class="setup-option-text">
                <div class="setup-option-title">Auto-Lock (60s)</div>
                <div class="setup-option-desc">Lock after 60 seconds of inactivity</div>
            </div>
            <div class="setup-option-check checked" id="autoLockCheck"></div>
        </div>
        <button class="btn btn-primary btn-full" style="margin-top:20px;" id="finishSetupBtn" onclick="finishSetup()" disabled>Continue</button>
    </div>
</div>

<!-- Auto-lock timer bar -->
<div class="auto-lock-bar" id="autoLockBar" style="width:100%; display:none;"></div>
"""

html = html.replace("<canvas id=\"bg-canvas\">", LOCK_SCREEN + "\n<canvas id=\"bg-canvas\">", 1)

# ═══ 3. Add security JS (before the init() call) ═══
SECURITY_JS = """
// ═══════════════════════════════════════════════
// SECURITY: PIN + Biometric + Auto-Lock
// ═══════════════════════════════════════════════

let securityConfig = {
    pinHash: null,        // SHA-256 hash of the PIN
    biometricEnabled: false,
    autoLockEnabled: true,
    autoLockSeconds: 60,
    biometricCredential: null,
};
let pinInput = '';
let pinSetupStep = 0; // 0=none, 1=enter, 2=confirm
let pinSetupFirst = '';
let isLocked = false;
let lastActivity = Date.now();
let autoLockTimer = null;
let autoLockBarTimer = null;

// SHA-256 hash
async function sha256(text) {
    const enc = new TextEncoder().encode(text);
    const buf = await crypto.subtle.digest('SHA-256', enc);
    return Array.from(new Uint8Array(buf)).map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');
}

// Load security config
function loadSecurityConfig() {
    const saved = localStorage.getItem('verdis_security');
    if (saved) {
        try { securityConfig = JSON.parse(saved); return true; } catch(e) {}
    }
    return false;
}

function saveSecurityConfig() {
    localStorage.setItem('verdis_security', JSON.stringify(securityConfig));
}

// Check if biometric is available (WebAuthn)
function checkBiometricSupport() {
    if (window.PublicKeyCredential && window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable) {
        window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable().then(function(available) {
            if (available) {
                document.getElementById('biometricSetupOption').style.display = 'flex';
                document.getElementById('biometricBtn').style.display = 'flex';
                if (securityConfig.biometricEnabled) {
                    // Auto-trigger biometric on lock
                    setTimeout(function() { unlockBiometric(); }, 300);
                }
            }
        });
    }
}

// ═══ Lock / Unlock ═══
function lockWallet() {
    if (!securityConfig.pinHash) return; // No PIN set, don't lock
    isLocked = true;
    pinInput = '';
    updatePinDisplay();
    document.getElementById('lockScreen').classList.remove('hidden');
    document.getElementById('lockTitle').textContent = 'Enter PIN';
    document.getElementById('lockSubtitle').textContent = 'Enter your 6-digit PIN to unlock';
    document.getElementById('lockError').classList.remove('show');
    if (securityConfig.biometricEnabled) {
        setTimeout(function() { unlockBiometric(); }, 300);
    }
}

function unlockWallet() {
    isLocked = false;
    document.getElementById('lockScreen').classList.add('hidden');
    lastActivity = Date.now();
    startAutoLockTimer();
    updateUI();
}

// ═══ PIN Input ═══
function pinPress(num) {
    if (pinInput.length >= 6) return;
    pinInput += num;
    updatePinDisplay();
    if (pinInput.length === 6) {
        setTimeout(function() { verifyPin(); }, 150);
    }
}

function pinClear() {
    pinInput = '';
    updatePinDisplay();
    document.getElementById('lockError').classList.remove('show');
}

function updatePinDisplay() {
    const dots = document.querySelectorAll('#pinDisplay .pin-dot');
    dots.forEach(function(dot, i) {
        if (i < pinInput.length) dot.classList.add('filled');
        else dot.classList.remove('filled');
    });
}

async function verifyPin() {
    const hash = await sha256(pinInput);
    if (hash === securityConfig.pinHash) {
        pinInput = '';
        updatePinDisplay();
        unlockWallet();
    } else {
        document.getElementById('lockError').textContent = 'Incorrect PIN. Try again.';
        document.getElementById('lockError').classList.add('show');
        document.getElementById('pinDisplay').classList.add('shake');
        setTimeout(function() { document.getElementById('pinDisplay').classList.remove('shake'); }, 300);
        pinInput = '';
        updatePinDisplay();
    }
}

// ═══ PIN Setup ═══
function startPinSetup() {
    pinSetupStep = 1;
    pinInput = '';
    pinSetupFirst = '';
    document.getElementById('setupScreen').classList.add('hidden');
    document.getElementById('lockScreen').classList.remove('hidden');
    document.getElementById('lockTitle').textContent = 'Create PIN';
    document.getElementById('lockSubtitle').textContent = 'Enter a 6-digit PIN';
    document.getElementById('lockError').classList.remove('show');
    updatePinDisplay();
}

// Handle PIN input during setup
async function handlePinSetupComplete() {
    if (pinSetupStep === 1) {
        pinSetupFirst = pinInput;
        pinInput = '';
        pinSetupStep = 2;
        updatePinDisplay();
        document.getElementById('lockTitle').textContent = 'Confirm PIN';
        document.getElementById('lockSubtitle').textContent = 'Re-enter your 6-digit PIN';
    } else if (pinSetupStep === 2) {
        if (pinInput === pinSetupFirst) {
            const hash = await sha256(pinInput);
            securityConfig.pinHash = hash;
            saveSecurityConfig();
            pinInput = '';
            pinSetupStep = 0;
            updatePinDisplay();
            document.getElementById('lockScreen').classList.add('hidden');
            document.getElementById('pinSetupCheck').classList.add('checked');
            document.getElementById('finishSetupBtn').disabled = false;
            document.getElementById('setupScreen').classList.remove('hidden');
            document.getElementById('lockTitle').textContent = 'Enter PIN';
            document.getElementById('lockSubtitle').textContent = 'Enter your 6-digit PIN to unlock';
            toast('PIN set successfully', 'success');
        } else {
            document.getElementById('lockError').textContent = 'PINs do not match. Start again.';
            document.getElementById('lockError').classList.add('show');
            document.getElementById('pinDisplay').classList.add('shake');
            setTimeout(function() { document.getElementById('pinDisplay').classList.remove('shake'); }, 300);
            pinInput = '';
            pinSetupStep = 1;
            pinSetupFirst = '';
            updatePinDisplay();
            document.getElementById('lockTitle').textContent = 'Create PIN';
            document.getElementById('lockSubtitle').textContent = 'Enter a 6-digit PIN';
        }
    }
}

// ═══ Biometric ═══
function toggleBiometricSetup() {
    if (securityConfig.biometricEnabled) {
        securityConfig.biometricEnabled = false;
        document.getElementById('biometricSetupCheck').classList.remove('checked');
        saveSecurityConfig();
    } else {
        registerBiometric();
    }
}

async function registerBiometric() {
    if (!window.PublicKeyCredential) {
        toast('Biometric not supported on this device', 'error');
        return;
    }
    try {
        const challenge = new Uint8Array(32);
        crypto.getRandomValues(challenge);
        const cred = await navigator.credentials.create({
            publicKey: {
                challenge: challenge,
                rp: { name: 'Verdis Wallet' },
                user: {
                    id: new Uint8Array(16),
                    name: 'verdis_user',
                    displayName: 'Verdis Wallet User',
                },
                pubKeyCredParams: [{ type: 'public-key', alg: -7 }],
                authenticatorSelection: {
                    authenticatorAttachment: 'platform',
                    userVerification: 'required',
                },
                timeout: 60000,
            }
        });
        securityConfig.biometricEnabled = true;
        securityConfig.biometricCredential = { id: cred.id, type: cred.type };
        saveSecurityConfig();
        document.getElementById('biometricSetupCheck').classList.add('checked');
        toast('Biometric enabled', 'success');
    } catch(e) {
        toast('Biometric setup cancelled', 'error');
    }
}

async function unlockBiometric() {
    if (!securityConfig.biometricEnabled || !securityConfig.biometricCredential) {
        toast('Biometric not configured', 'error');
        return;
    }
    try {
        const challenge = new Uint8Array(32);
        crypto.getRandomValues(challenge);
        await navigator.credentials.get({
            publicKey: {
                challenge: challenge,
                allowCredentials: [{
                    id: new Uint8Array(securityConfig.biometricCredential.id),
                    type: 'public-key',
                    transports: ['internal'],
                }],
                userVerification: 'required',
                timeout: 30000,
            }
        });
        unlockWallet();
    } catch(e) {
        // User cancelled biometric, stay on PIN
    }
}

// ═══ Auto-Lock ═══
function toggleAutoLock() {
    securityConfig.autoLockEnabled = !securityConfig.autoLockEnabled;
    document.getElementById('autoLockCheck').classList.toggle('checked');
    saveSecurityConfig();
}

function startAutoLockTimer() {
    if (autoLockTimer) clearInterval(autoLockTimer);
    if (autoLockBarTimer) clearInterval(autoLockBarTimer);
    if (!securityConfig.autoLockEnabled || isLocked) return;
    
    document.getElementById('autoLockBar').style.display = 'block';
    document.getElementById('autoLockBar').style.width = '100%';
    lastActivity = Date.now();
    
    autoLockBarTimer = setInterval(function() {
        const elapsed = (Date.now() - lastActivity) / 1000;
        const remaining = securityConfig.autoLockSeconds - elapsed;
        const pct = Math.max(0, (remaining / securityConfig.autoLockSeconds) * 100);
        document.getElementById('autoLockBar').style.width = pct + '%';
        if (remaining <= 0) {
            lockWallet();
            document.getElementById('autoLockBar').style.display = 'none';
        }
    }, 100);
}

function resetActivityTimer() {
    lastActivity = Date.now();
}

// Activity tracking
document.addEventListener('click', resetActivityTimer);
document.addEventListener('touchstart', resetActivityTimer);
document.addEventListener('keydown', resetActivityTimer);

// ═══ Setup Flow ═══
function finishSetup() {
    document.getElementById('setupScreen').classList.add('hidden');
    if (!wallet) {
        openModal('createModal');
    } else {
        updateUI();
    }
}

// ═══ Security settings in settings modal ═══
function updateSecuritySettings() {
    if (!document.getElementById('securitySettingsContent')) return;
    var pinStatus = securityConfig.pinHash ? '<span style="color:var(--accent-green);">Enabled</span>' : '<span style="color:var(--accent-red);">Not set</span>';
    var bioStatus = securityConfig.biometricEnabled ? '<span style="color:var(--accent-green);">Enabled</span>' : '<span style="color:var(--text-muted);">Disabled</span>';
    var lockStatus = securityConfig.autoLockEnabled ? '<span style="color:var(--accent-green);">60s</span>' : '<span style="color:var(--text-muted);">Off</span>';
    
    document.getElementById('securitySettingsContent').innerHTML = 
        '<div style="margin-bottom:16px;">' +
        '<div class="input-label" style="margin-bottom:10px;">Security Status</div>' +
        '<div style="display:flex; flex-direction:column; gap:8px;">' +
        '<div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-input); border:1px solid var(--border-color);"><span style="font-size:0.82rem;">PIN Protection</span>' + pinStatus + '</div>' +
        '<div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-input); border:1px solid var(--border-color);"><span style="font-size:0.82rem;">Biometric Unlock</span>' + bioStatus + '</div>' +
        '<div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-input); border:1px solid var(--border-color);"><span style="font-size:0.82rem;">Auto-Lock</span>' + lockStatus + '</div>' +
        '</div></div>' +
        '<button class="btn btn-primary btn-full" onclick="changePin()" style="margin-bottom:8px;">Change PIN</button>' +
        '<button class="btn btn-secondary btn-full" onclick="toggleBiometricSetup()" style="margin-bottom:8px;">' + (securityConfig.biometricEnabled ? 'Disable Biometric' : 'Enable Biometric') + '</button>' +
        '<button class="btn btn-secondary btn-full" onclick="toggleAutoLock()" style="margin-bottom:8px;">' + (securityConfig.autoLockEnabled ? 'Disable Auto-Lock' : 'Enable Auto-Lock') + '</button>' +
        '<button class="btn btn-danger btn-full" onclick="clearWallet()">Remove Wallet & Security</button>' +
        '<a href="/" class="btn btn-secondary btn-full" style="margin-top:8px;">Back to Home</a>';
}

function changePin() {
    closeModal('settingsModal');
    securityConfig.pinHash = null;
    saveSecurityConfig();
    startPinSetup();
}

"""

# Insert security JS before the init() call
html = html.replace("// Start the app\ninit();", SECURITY_JS + "\n// Start the app\ninit();", 1)

# ═══ 4. Override pinPress to handle setup mode ═══
# We need to intercept the pinPress function to handle setup vs unlock
html = html.replace(
    "function pinPress(num) {\n    if (pinInput.length >= 6) return;\n    pinInput += num;\n    updatePinDisplay();\n    if (pinInput.length === 6) {\n        setTimeout(function() { verifyPin(); }, 150);\n    }\n}",
    """function pinPress(num) {
    if (pinInput.length >= 6) return;
    pinInput += num;
    updatePinDisplay();
    if (pinInput.length === 6) {
        if (pinSetupStep > 0) {
            setTimeout(function() { handlePinSetupComplete(); }, 150);
        } else {
            setTimeout(function() { verifyPin(); }, 150);
        }
    }
}"""
)

# ═══ 5. Override clearWallet to also clear security ═══
html = html.replace(
    "function clearWallet() {\n    localStorage.removeItem('verdis_wallet');\n    wallet = null;\n    closeModal('settingsModal');\n    toast('Wallet removed', 'success');\n    updateUI();\n}",
    """function clearWallet() {
    localStorage.removeItem('verdis_wallet');
    localStorage.removeItem('verdis_security');
    wallet = null;
    securityConfig = { pinHash: null, biometricEnabled: false, autoLockEnabled: true, autoLockSeconds: 60, biometricCredential: null };
    isLocked = false;
    closeModal('settingsModal');
    document.getElementById('lockScreen').classList.add('hidden');
    document.getElementById('setupScreen').classList.add('hidden');
    toast('Wallet and security data removed', 'success');
    setTimeout(function() { location.reload(); }, 1000);
}"""
)

# ═══ 6. Update init() to check security first ═══
html = html.replace(
    """function init() {
    if (!loadWallet()) {
        openModal('createModal');
    }
    updateUI();
    
    // Auto-refresh
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(updateUI, 15000);
}""",
    """function init() {
    loadSecurityConfig();
    checkBiometricSupport();
    
    if (!securityConfig.pinHash) {
        // First time: show security setup
        document.getElementById('setupScreen').classList.remove('hidden');
        if (!loadWallet()) {
            // No wallet and no PIN — will create after setup
            document.getElementById('finishSetupBtn').textContent = 'Create Wallet';
        }
    } else {
        // Returning user: show lock screen
        document.getElementById('lockScreen').classList.remove('hidden');
        isLocked = true;
    }
    
    updateUI();
    
    // Auto-refresh
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(function() {
        if (!isLocked) updateUI();
    }, 15000);
}"""
)

# ═══ 7. Add security badge to header ═══
html = html.replace(
    '<span class="header-logo-text">VERDIS</span>',
    '<span class="header-logo-text">VERDIS</span><span class="security-badge" id="securityBadge" style="display:none;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>Secure</span>'
)

# ═══ 8. Update settings to include security tab ═══
html = html.replace(
    "document.getElementById('settingsContent').innerHTML =",
    "if (document.getElementById('securitySettingsContent')) updateSecuritySettings();\n        document.getElementById('settingsContent').innerHTML ="
)

# ═══ 9. Show security badge after unlock ═══
html = html.replace(
    "function unlockWallet() {\n    isLocked = false;",
    "function unlockWallet() {\n    isLocked = false;\n    document.getElementById('securityBadge').style.display = 'inline-flex';"
)

with open("/opt/verdis/app/dist/web/wallet.html", "w") as f:
    f.write(html)

# Verify
print("Security CSS added:", "lock-screen" in html)
print("Lock screen HTML:", 'id="lockScreen"' in html)
print("Setup screen HTML:", 'id="setupScreen"' in html)
print("Security JS added:", "sha256" in html)
print("PIN keypad:", "pinPress" in html)
print("Biometric:", "unlockBiometric" in html)
print("Auto-lock:", "autoLockTimer" in html)
print("File size:", f"{len(html):,} bytes")
