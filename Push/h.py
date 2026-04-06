import base64
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# создаём EC ключ P-256
private_key = ec.generate_private_key(ec.SECP256R1())

# приватный ключ (32 байта)
private_bytes = private_key.private_numbers().private_value.to_bytes(32, "big")

# публичный ключ
public_key = private_key.public_key()

public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# base64url
public_b64 = base64.urlsafe_b64encode(public_bytes).decode().rstrip("=")
private_b64 = base64.urlsafe_b64encode(private_bytes).decode().rstrip("=")

keys = {
    "public": public_b64,
    "private": private_b64
}

with open("vapid.json", "w") as f:
    json.dump(keys, f, indent=2)

print("PUBLIC:", public_b64)
print("PRIVATE:", private_b64)