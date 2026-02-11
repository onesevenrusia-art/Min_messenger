"""from aiohttp import web
import ssl

async def handle(request):
    return web.Response(text='Hello HTTPS!')

app = web.Application()
app.router.add_get('/', handle)

# SSL контекст
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(
    r'C:\Certbot\live\basicmimimummessenger.duckdns.org\fullchain.pem',
    r'C:\Certbot\live\basicmimimummessenger.duckdns.org\privkey.pem'
)

web.run_app(app, port=443, ssl_context=ssl_context)
"""
import os
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("testpush.html", {"request": request})

@app.get('/static/js/sw.js')
async def send_swjs():
    file_path = os.path.join("static", "js", "sw.js")
    if not os.path.exists(file_path):
        return Response(
            content="// Service Worker file not found",
            media_type="application/javascript",
            status_code=404
        )
    return FileResponse(
        file_path,
        media_type="application/javascript",
        filename="sw.js"
    )

@app.get('/static/{path:path}')
def send_static(path: str):
    return FileResponse(f'static/{path}')

if __name__ == "__main__":
    # Явно указываем ssl контекст как в aiohttp
    import ssl
    
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(
        r'C:\Certbot\live\basicmimimummessenger.duckdns.org\fullchain.pem',
        r'C:\Certbot\live\basicmimimummessenger.duckdns.org\privkey.pem'
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_version=ssl.PROTOCOL_TLS,
        ssl_cert_reqs=ssl.CERT_NONE,
        ssl_certfile=r'C:\Certbot\live\basicmimimummessenger.duckdns.org\fullchain.pem',
        ssl_keyfile=r'C:\Certbot\live\basicmimimummessenger.duckdns.org\privkey.pem',
        ssl_ciphers="ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20"
    )