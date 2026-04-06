from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import uvicorn, ssl
import os

directory = "media"
os.makedirs(directory, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/static/{path:path}')
def send_static(path: str):
    return FileResponse(f'static/{path}')

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