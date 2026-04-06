import os
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid01
from pywebpush import webpush
import uvicorn
import ssl, base64
app = FastAPI()

KEY_FILE = "vapid.json"
templates = Jinja2Templates(directory="templates")

if not os.path.exists(KEY_FILE):


    private_key = ec.generate_private_key(ec.SECP256R1())
    private_bytes = private_key.private_numbers().private_value.to_bytes(32, "big")
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    public_b64 = base64.urlsafe_b64encode(public_bytes).decode().rstrip("=")
    private_b64 = base64.urlsafe_b64encode(private_bytes).decode().rstrip("=")

    keys = {
        "public": public_b64,
        "private": private_b64
    }

    with open(KEY_FILE, "w") as f:
        json.dump(keys, f)

    print("VAPID keys generated")

else:
    print("VAPID keys loaded")


with open(KEY_FILE) as f:
    KEYS = json.load(f)

PUBLIC_KEY = KEYS["public"]
PRIVATE_KEY = KEYS["private"]

# временное хранение подписки
subscription_data = None

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/public")
def public(request: Request):
    return {"key":PUBLIC_KEY}

@app.get('/static/{path:path}')
def send_static(path: str):
    return FileResponse(f'static/{path}')

@app.get("/push_key")
async def push_key():
    return {"key": PUBLIC_KEY}


# -----------------------------
# сохранить подписку
# -----------------------------

@app.post("/subscribe")
async def subscribe(sub: dict):

    global subscription_data
    subscription_data = sub

    print("subscription saved")

    return {"status": "ok"}

@app.get("/send")
async def send_push():

    if not subscription_data:
        print("error")
        return {"error": "no subscription"}

    r = webpush(
        subscription_info=subscription_data,
        data=json.dumps({
            "title": "Новое сообщение",
            "body": "Push работает 🚀"
        }),
        vapid_private_key=PRIVATE_KEY,
        vapid_claims={
            "sub": "mailto:test@test.com"
        }
    )
    print(r)
    return {"status": "push sent"}
if __name__ == "__main__":    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_version=ssl.PROTOCOL_TLS,
        ssl_cert_reqs=ssl.CERT_NONE,
        ssl_certfile=r'fullchain.pem',
        ssl_keyfile=r'privkey.pem',
        ssl_ciphers="ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20"
    ) 