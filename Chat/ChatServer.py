from fastapi import FastAPI, WebSocket, Request
import uvicorn
import json
app = FastAPI()


clients = {}
clientsoffline={}
wait_for = {}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket): 
    await ws.accept()

    device_id = ws.client.host
    print(device_id)
    if not device_id:
        await ws.close()
        return

    print(f"[WS] Connected: {device_id}")
    clients[device_id] = {"ws":ws}
    try:
        if device_id in wait_for:
            for message in wait_for[device_id]:
                await clients[device_id]["ws"].send_json(message)
    except:
            pass
    try:
        while True:
            msg = await ws.receive_text()
            
            for key in clients.keys():
                if key==device_id:continue
                client=clients[key]
                await client["ws"].send_json({"type":"message","ip":key,"message":msg["message"],"time":msg["time"]})

            print(f"[WS] From {device_id}: {msg}")

    except Exception:
        print(f"[WS] Disconnected: {device_id}")

    finally:
        
        clients.pop(device_id, None)



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    
    )