from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Load the key
with open("chicken_openssh_key.pem", "rb") as f:
    key = serialization.load_pem_private_key(f.read(), password=None)

# Now use `key` to decrypt or derive the flag, depending on the challenge
