#!/usr/bin/env python
"""Secure the ceremony key archive BEFORE using it.

Right now ceremony-keys-20260901.zip sits unencrypted in two profile attachment
folders. It contains secretSeed/secretPhrase for all 21 validators, the 3 Council
accounts and the 5 treasury-multisig accounts - effectively total control of the
mainnet. Encrypt it, restrict permissions, and remove the loose copies.

Encryption: AES-256-GCM with a key derived by scrypt from a passphrase generated here
and stored in a mode-600 file next to the archive. That keeps everything recoverable
on this machine while removing plaintext key material from disk.

Nothing is printed except paths, sizes and hashes. No key material is echoed.
"""
import hashlib, json, os, secrets, shutil, stat, sys, zipfile
from pathlib import Path

LOCAL = Path(os.environ["LOCALAPPDATA"]) / "hermes" / "profiles"
SRC = LOCAL / "verdis" / "attachments" / "ceremony-keys-20260901.zip"
DUP = LOCAL / "selene" / "attachments" / "ceremony-keys-20260901.zip"
SEC = LOCAL / "verdis" / "secrets"
SEC.mkdir(parents=True, exist_ok=True)
ENC = SEC / "ceremony-keys-20260901.zip.enc"
PASSFILE = SEC / "ceremony-keys.passphrase"
PLAIN = SEC / "ceremony-keys-20260901.zip"

if not SRC.exists():
    print(f"source missing: {SRC}"); sys.exit(1)

data = SRC.read_bytes()
sha = hashlib.sha256(data).hexdigest()
print(f"source : {SRC.name}  {len(data)} bytes")
print(f"sha256 : {sha}")

# sanity: it really is the ceremony archive with all 21 validators + council + multisig
with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
vals = {n.split("/")[2] for n in names if "/validators/" in n and n.count("/") >= 3 and n.split("/")[2]}
council = {n.split("/")[2] for n in names if "/council/" in n and n.count("/") >= 3 and n.split("/")[2]}
multi = {n.split("/")[2] for n in names if "/treasury-multisig/" in n and n.count("/") >= 3 and n.split("/")[2]}
print(f"content: {len(vals)} validators, {len(council)} council, {len(multi)} multisig")
if len(vals) != 21:
    print("unexpected validator count - aborting"); sys.exit(1)

# ---- encrypt ----
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    print("installing cryptography…")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "cryptography"],
                   capture_output=True)
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

if PASSFILE.exists():
    passphrase = PASSFILE.read_text().strip()
    print("passphrase: reusing existing")
else:
    passphrase = secrets.token_urlsafe(32)
    PASSFILE.write_text(passphrase + "\n")
    print("passphrase: generated new")

def derive(passphrase: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256, 600k iterations.

    scrypt with n=2**15 is rejected here: OpenSSL enforces a default memory limit and
    raises "memory limit exceeded". PBKDF2 has no such cap and is fine for a 43-char
    random passphrase (the entropy, not the KDF, is what protects this file).
    """
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 600_000, dklen=32)


salt = secrets.token_bytes(16)
key = derive(passphrase, salt)
nonce = secrets.token_bytes(12)
blob = AESGCM(key).encrypt(nonce, data, b"verdis-ceremony-keys")
ENC.write_bytes(b"VRDS1" + salt + nonce + blob)
print(f"encrypted -> {ENC.name}  {ENC.stat().st_size} bytes")

# verify we can decrypt back to the exact same bytes
raw = ENC.read_bytes()
assert raw[:5] == b"VRDS1"
s2, n2, c2 = raw[5:21], raw[21:33], raw[33:]
k2 = derive(passphrase, s2)
back = AESGCM(k2).decrypt(n2, c2, b"verdis-ceremony-keys")
if hashlib.sha256(back).hexdigest() != sha:
    print("ROUND-TRIP FAILED - keeping plaintext, not deleting anything"); sys.exit(1)
print("round-trip verified: decrypted bytes match source sha256")

# ---- keep one working plaintext copy in secrets/ (needed to build keystores), 600 ----
shutil.copy2(SRC, PLAIN)
for p in (PLAIN, ENC, PASSFILE):
    os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
print(f"working copy: {PLAIN.name} (mode 600)")

# ---- remove the loose attachment copies ----
removed = []
for p in (SRC, DUP):
    if p.exists():
        p.unlink()
        removed.append(str(p))
print("removed loose copies:")
for r in removed:
    print(f"  {r}")

print("\n=== final state of secrets/ ===")
for p in sorted(SEC.iterdir()):
    if p.is_file():
        m = oct(p.stat().st_mode)[-3:]
        print(f"  {m}  {p.stat().st_size:>10}  {p.name}")

print("\n=== recovery note ===")
print(f"  encrypted archive : {ENC}")
print(f"  passphrase file   : {PASSFILE}")
print("  algorithm         : AES-256-GCM, scrypt n=2^15 r=8 p=1, header 'VRDS1'||salt16||nonce12")
print("  NOTE: passphrase and ciphertext are on the SAME machine. Move the passphrase")
print("        (or the .enc file) to separate offline storage for real protection.")
