from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import ssl
app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("testgr.html", {"request": request})

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