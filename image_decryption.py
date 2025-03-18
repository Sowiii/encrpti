from cryptography.fernet import Fernet

# Load the encryption key
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

def decrypt_image(encrypted_path, output_path):
    """Decrypt an encrypted image file"""
    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_path, "wb") as file:
        file.write(decrypted_data)

    print(f"✅ Image decrypted and saved as {output_path}")

# Example Usage:
decrypt_image("encrypted_image.enc", "decrypted_output.jpg")
