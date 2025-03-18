from cryptography.fernet import Fernet

# Load the encryption key
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

def encrypt_image(image_path, output_path):
    """Encrypt an image file"""
    with open(image_path, "rb") as file:
        image_data = file.read()

    encrypted_data = cipher.encrypt(image_data)

    with open(output_path, "wb") as file:
        file.write(encrypted_data)

    print(f"✅ Image encrypted and saved as {output_path}")

# Example Usage:
encrypt_image("input.jpg", "encrypted_image.enc")
