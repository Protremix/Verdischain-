use crate::error::{CoreError, CoreResult};
use ed25519_dalek::{Keypair, PublicKey, SecretKey, Signer, Signature};
use sha2::{Sha256, Digest};
use hex;

/// Keystore entry — holds an encrypted keypair
#[derive(Clone)]
pub struct Account {
    pub address: String,
    pub public_key: [u8; 32],
    encrypted_secret: Vec<u8>,
    pub name: String,
}

impl Account {
    /// Generate a new Ed25519 keypair from random entropy
    pub fn generate(name: &str, pin: &str) -> CoreResult<Self> {
        let mut csprng = rand::rngs::OsRng {};
        let keypair = Keypair::generate(&mut csprng);
        Self::from_keypair(name, pin, &keypair)
    }

    /// Import a keypair from a 32-byte seed (hex or raw)
    pub fn from_seed(name: &str, pin: &str, seed_hex: &str) -> CoreResult<Self> {
        let seed_bytes = hex::decode(seed_hex.strip_prefix("0x").unwrap_or(seed_hex))?;
        if seed_bytes.len() != 32 {
            return Err(CoreError::InvalidKey(format!("Seed must be 32 bytes, got {}", seed_bytes.len())));
        }
        let mut seed_array = [0u8; 32];
        seed_array.copy_from_slice(&seed_bytes);
        let secret = SecretKey::from_bytes(&seed_array)
            .map_err(|e| CoreError::InvalidKey(format!("{}", e)))?;
        let public = PublicKey::from(&secret);
        let keypair = Keypair { secret, public };
        Self::from_keypair(name, pin, &keypair)
    }

    /// Import from a mnemonic seed phrase (BIP39-style)
    pub fn from_mnemonic(name: &str, pin: &str, mnemonic: &str) -> CoreResult<Self> {
        let mut hasher = Sha256::new();
        hasher.update(mnemonic.as_bytes());
        let seed: [u8; 32] = hasher.finalize().into();
        let seed_hex = hex::encode(seed);
        Self::from_seed(name, pin, &seed_hex)
    }

    fn from_keypair(name: &str, pin: &str, keypair: &Keypair) -> CoreResult<Self> {
        let pubkey_bytes = keypair.public.to_bytes();
        let address = crate::ss58::encode_address(&pubkey_bytes, crate::ss58::VERDIS_SS58_PREFIX);
        let encrypted = encrypt_secret(&keypair.secret.to_bytes(), pin)?;
        Ok(Account {
            address,
            public_key: keypair.public.to_bytes(),
            encrypted_secret: encrypted,
            name: name.to_string(),
        })
    }

    /// Decrypt the secret key with PIN and return the keypair
    pub fn unlock(&self, pin: &str) -> CoreResult<Keypair> {
        let secret_bytes = decrypt_secret(&self.encrypted_secret, pin)?;
        let secret = SecretKey::from_bytes(&secret_bytes)
            .map_err(|e| CoreError::InvalidKey(format!("{}", e)))?;
        let public = PublicKey::from(&secret);
        Ok(Keypair { secret, public })
    }

    /// Export the raw private key (hex) — requires PIN
    pub fn export_private_key(&self, pin: &str) -> CoreResult<String> {
        let secret_bytes = decrypt_secret(&self.encrypted_secret, pin)?;
        Ok(hex::encode(secret_bytes))
    }

    /// Export the public key as hex
    pub fn public_key_hex(&self) -> String {
        hex::encode(self.public_key)
    }

    /// Sign a message with the unlocked keypair
    pub fn sign(&self, pin: &str, message: &[u8]) -> CoreResult<[u8; 64]> {
        let keypair = self.unlock(pin)?;
        let sig: Signature = keypair.sign(message);
        Ok(sig.to_bytes())
    }
}

fn encrypt_secret(secret: &[u8; 32], pin: &str) -> CoreResult<Vec<u8>> {
    let key = derive_pin_key(pin);
    let mut encrypted = Vec::with_capacity(32);
    for (i, &byte) in secret.iter().enumerate() {
        encrypted.push(byte ^ key[i % key.len()]);
    }
    Ok(encrypted)
}

fn decrypt_secret(encrypted: &[u8], pin: &str) -> CoreResult<[u8; 32]> {
    if encrypted.len() != 32 {
        return Err(CoreError::InvalidKey("Encrypted key is corrupted".into()));
    }
    let key = derive_pin_key(pin);
    let mut secret = [0u8; 32];
    for (i, &byte) in encrypted.iter().enumerate() {
        secret[i] = byte ^ key[i % key.len()];
    }
    Ok(secret)
}

fn derive_pin_key(pin: &str) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(pin.as_bytes());
    hasher.update(b"verdis-salt-v2");
    hasher.finalize().to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_and_unlock() {
        let account = Account::generate("test", "123456").unwrap();
        assert!(account.address.len() > 40);
        let keypair = account.unlock("123456").unwrap();
        assert_eq!(keypair.public.to_bytes(), account.public_key);
    }

    #[test]
    fn test_from_seed() {
        let seed = "a1a2a3a4a5a6a7a8a9a0b1b2b3b4b5b6b7b8b9b0c1c2c3c4c5c6c7c8c9d0d1d2";
        let account = Account::from_seed("test", "123456", seed).unwrap();
        assert_eq!(account.public_key.len(), 32);
        let keypair = account.unlock("123456").unwrap();
        assert_eq!(keypair.public.to_bytes(), account.public_key);
    }

    #[test]
    fn test_sign_verify() {
        let account = Account::generate("test", "123456").unwrap();
        let message = b"hello verdis";
        let signature = account.sign("123456", message).unwrap();
        assert_eq!(signature.len(), 64);

        use ed25519_dalek::Verifier;
        let public = PublicKey::from_bytes(&account.public_key).unwrap();
        let sig = ed25519_dalek::Signature::from_bytes(&signature).unwrap();
        assert!(public.verify(message, &sig).is_ok());
    }
}
