from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import ssl
app = FastAPI()

clients = []
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def ws(ws: WebSocket):

    await ws.accept()
    clients.append(ws)

    try:
        while True:
            data = await ws.receive_text()

            for c in clients:
                if c != ws:
                    await c.send_text(data)

    except:
        clients.remove(ws)

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