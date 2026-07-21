from cryptography.hazmat.primitives import serialization

# 1. EC private key-г файл-аас унших
with open("chicken_openssh_key.pem", "rb") as f:
    pem_data = f.read()

# Private key-г load хийх
private_key = serialization.load_pem_private_key(pem_data, password=None)

# 2. Public key-г гаргах (жишээ)
public_key = private_key.public_key()
pub_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
print("Public key (hex):", pub_bytes.hex())

# 3. Flag decode хийх хэсэг
# Ихэвчлэн challenge-д cipher_text өгөгдсөн байдаг
# Жишээ:
# cipher_text = b"..."
# flag_bytes = private_key.exchange(ec.ECDH(), cipher_text)
# print("Flag:", flag_bytes.decode())
