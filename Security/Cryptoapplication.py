import sys, json, struct, os
import win32crypt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

KEY_FILE = "keys.dat"

# ---------------- Native messaging ----------------

def read_msg():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None
    msg_len = struct.unpack("<I", raw_len)[0]
    data = sys.stdin.buffer.read(msg_len)
    return json.loads(data.decode())

def send_msg(obj):
    data = json.dumps(obj).encode()
    sys.stdout.buffer.write(struct.pack("<I", len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

# ---------------- Key storage (DPAPI) ----------------

def save_keys(blob: bytes):
    encrypted = win32crypt.CryptProtectData(blob, None, None, None, None, 0)
    with open(KEY_FILE, "wb") as f:
        f.write(encrypted)

def load_keys() -> bytes | None:
    if not os.path.exists(KEY_FILE):
        return None
    with open(KEY_FILE, "rb") as f:
        encrypted = f.read()
    return win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1]

# ---------------- Crypto core ----------------

def generate_keys():
    sign_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    enc_key  = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    blob = json.dumps({
        "sign": sign_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ).decode(),
        "enc": enc_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ).decode()
    }).encode()

    save_keys(blob)
    return sign_key, enc_key

def load_or_create_keys():
    blob = load_keys()
    if blob is None:
        return generate_keys()

    data = json.loads(blob.decode())
    sign_key = serialization.load_pem_private_key(data["sign"].encode(), None)
    enc_key  = serialization.load_pem_private_key(data["enc"].encode(), None)
    return sign_key, enc_key

sign_key, enc_key = load_or_create_keys()

# ---------------- Operations ----------------

def get_public_keys():
    return {
        "signingPublicKey": base64.b64encode(
            sign_key.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).decode(),
        "encryptionPublicKey": base64.b64encode(
            enc_key.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).decode()
    }

def sign_challenge(challenge: str):
    sig = sign_key.sign(
        challenge.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
        hashes.SHA256()
    )
    return base64.b64encode(sig).decode()

def hybrid_decrypt(pkg):
    aes_key = enc_key.decrypt(
        base64.b64decode(pkg["encryptedKey"]),
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aes = AESGCM(aes_key)
    plaintext = aes.decrypt(
        base64.b64decode(pkg["iv"]),
        base64.b64decode(pkg["encryptedData"]),
        None
    )

    return plaintext.decode()

# ---------------- Main loop ----------------

while True:
    msg = read_msg()
    if msg is None:
        break

    try:
        t = msg["type"]

        if t == "getPublicKeys":
            send_msg(get_public_keys())

        elif t == "signChallenge":
            send_msg({"signature": sign_challenge(msg["challenge"])})

        elif t == "hybridDecrypt":
            send_msg({"plaintext": hybrid_decrypt(msg)})

        else:
            send_msg({"error": "unknown_command"})

    except Exception as e:
        send_msg({"error": str(e)})