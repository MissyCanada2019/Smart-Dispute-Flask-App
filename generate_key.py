#!/usr/bin/env python3
"""
Generates a new Fernet encryption key.
This key should be stored securely as an environment variable.
"""
from cryptography.fernet import Fernet

def generate_key():
    """Generates and prints a new encryption key."""
    key = Fernet.generate_key()
    print("--- Generated Encryption Key ---")
    print("==============================================================")
    print(key.decode())
    print("==============================================================")
    print("\n🚨 IMPORTANT: Store this key securely as the ENCRYPTION_KEY")
    print("environment variable in your production environment (e.g., Railway, .env file).")
    print("Do NOT commit this key to your version control system.")

if __name__ == "__main__":
    generate_key()