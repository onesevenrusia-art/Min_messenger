from fastapi import FastAPI, WebSocket, Request
import uvicorn

app = FastAPI()

# Подключённые клиенты: device_id -> WebSocket
clients = {}


# ===============================
#   WebSocket /ws (будет WSS)
# ===============================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    device_id = ws.query_params.get("device_id")
    if not device_id:
        await ws.close()
        return

    print(f"[WS] Connected: {device_id}")
    clients[device_id] = ws

    try:
        while True:
            msg = await ws.receive_text()
            print(f"[WS] From {device_id}: {msg}")

    except Exception:
        print(f"[WS] Disconnected: {device_id}")

    finally:
        clients.pop(device_id, None)


# ===============================
#     HTTP POST /notify
# ===============================
@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    device_id = data["device_id"]
    payload = data["payload"]

    if device_id in clients:
        try:
            await clients[device_id].send_json(payload)
            return {"status": "sent"}
        except:
            return {"status": "error"}
    else:
        return {"status": "offline"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem"
    )