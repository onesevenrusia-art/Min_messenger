from fastapi import FastAPI, WebSocket, Request
import uvicorn

app = FastAPI()

# Подключённые клиенты: device_id -> WebSocket
clients = {}
wait_for = {}

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
    clients[device_id] = {"ws":ws}
    try:
        if device_id in wait_for:
            for message in wait_for[device_id]:
                await clients[device_id]["ws"].send_json(message)
                wait_for[device_id].remove(message)
            
    except:
            pass
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
    device_id = data["email"]
    if device_id in clients:
        try:
            await clients[device_id]["ws"].send_json(data)
            return {"success":True,
                    "status": "sent"}
        except:
            return {"status": "error",
                    "success":False}
        
    else:
        if device_id not in wait_for:
            wait_for[device_id]=[]
        wait_for[device_id].append(data)

        return {
            "success":True,
            "status": "offline"
            }

@app.post("/cancel")
async def cancel(request: Request):
    data = await request.json()
    print(request.client.host)
    device_id = data["email"]
    if device_id in clients:
        try:
            if device_id in clients:
                for m in clients[device_id]["msgoffline"]:
                    if m["type"]=="newdevice":
                        clients[device_id]["msgoffline"].pop(m ,None)

            await clients[device_id+'newdevice']["ws"].close()
            return {"success":True,
                    "status": "sent"}
        except:pass
    return {"status": "error",
                    "success":False}
        
@app.post("/cancel_agree")
async def cancelb2(request: Request):
    data = await request.json()
    print(888)
    device_id = data["email"]
    if device_id in clients:
        try:
            await clients[device_id]["ws"].send_json({"type":"new_device","success":False})
            del clients[device_id]
            print(888,"ok")
            return {"type":"new_device","success":False}
        except:
            print(888,"error")
            pass
    else:
        print(888,"not in")
        if device_id not in wait_for:
            wait_for[device_id]=[]
        wait_for[device_id].append({"type":"new_device","success":False})        
        return {"success":True,
                    "status": "sent"}
    return {"status": "error",
                    "success":False}

@app.post("/i_agree")
async def keys_sent(request: Request):
    data = await request.json()
    print(888)
    device_id = data["email"]
    if device_id in clients:
        try:
            await clients[device_id]["ws"].send_json({"type":"new_device","success":True,"key":data["key"]})
            del clients[device_id]
            print(888,"ok")
            return {"success":True,
                    "status": "sent"}
        except:
            print(888,"error")
            pass
    else:
        print(888,"not in")
        if device_id not in wait_for:
            wait_for[device_id]=[]
        wait_for[device_id].append({"type":"new_device","success":True,"key":data["key"]})        
        return {"success":True,
                    "status": "sent"}
    return {"status": "error",
                    "success":False}



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem"
    )