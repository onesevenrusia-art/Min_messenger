from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from pywebpush import webpush
import smtplib
import json
import random
import MessengerDataBase
import FeedBacks
import uvicorn
import base64, uuid
import os, sys, traceback
import ssl

clients = {}
calls = {0:[]}
wait_for = {}
WebSocketDevices=[]
DoctypeKeys={}
DevicesKeys = {}
removedevicekeys={}
challenges_auth={}
challenges_del={}
challenges_prof={}
challenges_conn_device={}
passwordf = open("C:/Users/SB/Desktop/gmailpassword.txt").read()



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

app = FastAPI()
Database = MessengerDataBase.DataBaseManager()
feedbacksdb = FeedBacks.Feedback_Manager()
templates = Jinja2Templates(directory="templates")


def save_encrypted_media(payload: dict,id) -> str:
    media_id = id

    base_path = Path("media/encrypted")
    base_path.mkdir(parents=True, exist_ok=True)

    # --- paths ---
    data_path = base_path / f"{media_id}.bin"
    key_path  = base_path / f"{media_id}.key"
    iv_path   = base_path / f"{media_id}.iv"

    # --- decode base64 → bytes ---
    encrypted_data = base64.b64decode(payload["encryptedData"])
    encrypted_key  = base64.b64decode(payload["encryptedKey"])
    iv             = base64.b64decode(payload["iv"])

    # --- write RAW BYTES ---
    data_path.write_bytes(encrypted_data)
    key_path.write_bytes(encrypted_key)
    iv_path.write_bytes(iv)

    return media_id

def save_photo_to_folder(name, photo_base64):
    try:
        if not photo_base64:
            print("❌ Нет данных фото")
            return None
        if ',' in photo_base64:
            photo_base64 = photo_base64.split(',')[1]
        photo_bytes = base64.b64decode(photo_base64)
        upload_folder = 'UsersPhotos'
        os.makedirs(upload_folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{name}_{timestamp}_{unique_id}.jpg"
        filepath = f"{upload_folder}/{filename}"
        with open(filepath, 'wb') as f:
            f.write(photo_bytes)
        print(f"✅ Фото сохранено: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ Ошибка сохранения фото: {e}")
        return None

def verify_signature_simple(challenge, signature_b64, public_key_data):
    try:
        signature_bytes = base64.b64decode(signature_b64)
        public_key_pem = public_key_data.strip()
        if not public_key_pem.startswith('-----BEGIN'):
            public_key_bytes = base64.b64decode(public_key_pem)
            public_key_pem = f"""-----BEGIN PUBLIC KEY-----
{base64.b64encode(public_key_bytes).decode('utf-8')}
-----END PUBLIC KEY-----"""
        
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        
        public_key.verify(
            signature_bytes,
            challenge.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=32
            ),
            hashes.SHA256()
        )
        return True
        
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"Ошибка при проверке подписи: {e}")
        return False

def IsEmailCorrect(email):
    try:
        valid = validate_email(email)
        if valid:
            return True
        else:return False
    except EmailNotValidError:
        return False

def SendCode(emailreciver,body=0,flag=True):
    email_from = 'onesevenrusia@gmail.com' 
    password = passwordf 
    email_to = emailreciver
    code=str(random.randint(100000, 999999))
    print(code)
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = 'Ваш код подтверждения'
    if body==0:
        body = f"""
        Здравствуйте!
        Ваш код для подтверждения: <b>{code}</b>

        Никому не сообщайте этот код.
        """
    else:body=body
    msg.attach(MIMEText(body, 'html')) 
    try:
        # Создаем соединение с SMTP-сервером Gmail (порт 587 для TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Шифруем соединение
        server.login(email_from, password)  # Логинимся на сервер
        text = msg.as_string()  # Преобразуем сообщение в строку
        if flag:
            server.sendmail(email_from, email_to, text)  # Отправляем письмо
    except Exception as e:
        print(e)
        try:
            server.quit()
        except:pass
        return [True, code]
    finally:
        try:
            server.quit()
        except:pass
        return [True, code]


def SendWEBpush(notify, device_id=None,user_id=None,subscription_data = None):
    if subscription_data is not None:
            r = webpush(
                subscription_info=subscription_data,
                data=json.dumps(notify),
                vapid_private_key=PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:test@test.com"
                }
            )
            print(r)
            return r
    if device_id == "all":
        r=0
        for d in Database.get_user_devices(int(user_id)):
            if not d["subscription_data"] or d["subscription_data"] == {}:
                continue
            print(d)
            r = webpush(
                subscription_info=d["subscription_data"],
                data=json.dumps(notify),
                vapid_private_key=PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:test@test.com"
                }
            )
            print(r)
        return r
    else:
        d = Database.get_device_by_id(int(device_id))
        if not d["subscription_data"] or d["subscription_data"] == {}:
            return 
        r = webpush(
                subscription_info=d["subscription_data"],
                data=json.dumps(notify),
                vapid_private_key=PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:test@test.com"
                }
            )
        print(r)
        return r


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("RegisterUser.html", {"request": request})

@app.get("/messenger.html")
def index2(request: Request):
    return templates.TemplateResponse("messenger.html", {"request": request})

@app.get('/static/{path:path}')
def send_static(path: str):
    return FileResponse(f'static/{path}')
 
@app.get('/UsersPhotos/{path:path}')
def userphoto(path: str):
    return FileResponse(f'UsersPhotos/{path}')

@app.get('/media/{path:path}')
def usermedia(path: str):
    return FileResponse(f'media/{path}')

@app.get('/favicon.ico')
def favicon():
    return FileResponse('static/images/logo.png')

@app.get('/sw.js')
async def send_swjs():
    file_path = os.path.join("static", "js", "sw.js")
    if not os.path.exists(file_path):
        return Response(
            content="// Service Worker file not found",
            media_type="application/javascript",
            status_code=404
        )
    return FileResponse(
        "sw.js",
        media_type="application/javascript",
        filename="sw.js"
    )
#""


async def send_WS_msg(reciver, msg, wait=False, exception=[], need=[],notify=None):
    try:
        if reciver not in clients.keys():
            if wait:
                if reciver not in wait_for:
                    wait_for[reciver]=[]
                wait_for[reciver].append(msg)  
            return {
                "success":True,
                "status": "offline",
                "ids":["all"]
                }
        else:
            sent_count = 0
            ids=[]
            if len(need)==0:
                for devi in clients.get(reciver):
                    if devi["id"] not in list(map(str,exception)) and devi["id"] != "newdevice":
                        await devi["ws"].send_json(msg)
                        sent_count+=1
                        ids.append(devi["id"])
            else:
                for devi in clients.get(reciver):         
                    if devi["id"] in list(map(str,need)):
                        await devi["ws"].send_json(msg)
                        sent_count+=1
                        ids.append(devi["id"])
            if sent_count>0:
                return {"success":True,
                            "status": "sent","ids":ids}
            else:
                return {"status": "offline",
                        "success":False,"ids":ids}
    except Exception as e:
        print(242,e)
        return {"status": "error",
                    "success":False}



@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket): 
    await ws.accept()
    device_id = ws.query_params.get("device_id")
    if not device_id:
        await ws.close()
        return
    this_deviceid =device_id.split("|id")[1]
    this_email = device_id.split("|")[0]
    this_userid =int(Database.get_user_by_email(this_email)["id"])
    CurrentCallID = -1
    if "newdevice" in device_id:
        print(clients.get(this_email))
        if clients.get(this_email) is not None and this_deviceid in clients.get(this_email):
            await ws.close()
            return     
    else:
        if device_id not in WebSocketDevices:
            print("not in devices/clients",WebSocketDevices,clients,device_id)
            await ws.close()
            return     
    
    this_user = Database.get_user_by_email(this_email)
    print(f"[WS] Connected: {device_id}")
    if not clients.get(this_email):
        clients[this_email]=[]
    clients[this_email].append({"id":this_deviceid,"ws":ws})
    try:
        if this_email in wait_for and this_deviceid != "newdevice":
            for message in wait_for[this_email]:
                await ws.send_json(message)
                try:
                    wait_for[this_email][device_id].remove(message)
                except:pass
        #print(f'#{Database.get_user_Inventives(device_id.split("|")[0])}#')
        if this_deviceid != "newdevice":
            for inventive in Database.get_user_Inventives(this_email):
                inventive["time"]=inventive["time"].isoformat()
                if inventive["typeinventive"]=="newchat" and inventive["emailsent"] != this_email and int(inventive["status"])==0:
                    await ws.send_json({"type":"new_chat","user":inventive["emailsent"],"time":inventive["time"],"publickey":inventive["publickey"],"privatekey":inventive["reciverencryptedkey"]})
                if inventive["emailsent"] == this_email and this_deviceid != "newdevice" and int(inventive["status"])==1:
                    dvs=Database.get_user_devices(this_userid)
                    for dv in dvs:
                        if this_deviceid==dv["id"]:
                            needchat = Database.get_chat(inventive["message"]["chatid"])
                            await ws.send_json(
                                {"type":"addchat",
                                "chat":{"id":needchat["id"],
                                    "type":needchat["type"],
                                    "name":needchat["name"],
                                    "photo":needchat["photo"],
                                    "about":needchat["about"],
                                    "publickeycrypt":needchat["publickeycrypt"],
                                    "privatekeycrypt":inventive["senderencryptedkey"]}})
                            Database.update_reciver_inventive(inventive["id"],this_email,int(this_deviceid))
            print(this_deviceid,Database.get_device_by_id(int(this_deviceid)))
            for event in Database.get_Events_before(this_userid,Database.get_device_by_id(this_deviceid)["last_seen"]):
                await ws.send_json({
                    "type":"new_event",
                    "message": Database.get_message_by_id(event["msg_id"]),
                    "chat_id":event["chat_id"],
                    "datatime":event["datatime"]
                })

    except Exception as e:
        print(291,e,traceback.format_exc())
    try:
        while True:
            msg = await ws.receive_json()
            print(f"[WS] From {device_id}: xxxxx")
            print(msg)
            if msg["type"] == "newchat":
                if "newdevice" not in device_id and msg["email"] not in device_id:
                    ids=[]
                    if clients.get(msg["email"]) is not None:
                        for client in clients.get(msg["email"]):
                            try:
                                if client["id"]!="newdevice":
                                    await client["ws"].send_json({"type":"new_chat","user":device_id.split("|")[0]})
                                    ids.append(int(client["id"]))
                            except Exception as e:
                                print("248❌",e)
                        if len(ids)==0:
                            u=Database.get_user_by_email(msg["email"])
                            if u["photo"] == None:
                                u["photo"]="/static/images/Uniknown.png"
                            for d in u["devices"]:
                                if d["subscription_data"] is not None and d["subscription_data"] != {} and int(d["id"]) not in ids:
                                    print("start sendind")
                                    r=SendWEBpush(notify={
                                        "title":"Новый чат",
                                        "body":f'{u["name"]} хочет создать с вами чат',
                                        "icon":u["photo"]
                                        },subscription_data=d["subscription_data"])
                                    print("end sending",r)

                    flag=True
                    for inv in Database.get_user_Inventives(msg["email"]):
                        if inv["typeinventive"] == "newchat" and inv["emailsent"] == this_email:
                            flag=False
                            break
                    if flag:
                        ms_data = {
                            "chatid":"x",
                            "devices": [i['id'] for i in Database.get_user_devices(this_userid)]+[i['id'] for i in Database.get_user_devices(msg["email"])]
                        }
                        r=Database.add_Inventive(emailrecive=msg["email"],
                                            emailsent=device_id.split("|")[0],
                                            inventivetype="newchat",
                                            publickey=msg["publickey"],
                                            message=ms_data,
                                            reciverencryptedkey=str(msg["encrypted"]),
                                            senderencryptedkey=str(msg["myencrypted"])
                                            )
                        print(r)
                    await ws.send_json({"type":"answnewchat","success":"waiting"})
                else:
                    try:
                        print("error answ")
                        await ws.send_json({"type":"answnewchat","success":"error"})
                    except Exception as e:              
                        print("262❌",e)
            if msg["type"] == "newchatagree" or msg["type"] == "newchatdisagree":
                print(f"[Agree] ")
                sender = Database.get_user_by_email(msg["email"])
                reciver = Database.get_user_by_email(device_id.split("|")[0])
                for inventive in Database.get_user_Inventives(reciver["email"]):
                    if inventive["emailsent"]==msg["email"] and inventive["typeinventive"]=="newchat":
                        if msg["type"]=="newchatagree":
                            pbc = inventive["publickey"]
                            pvc = inventive["reciverencryptedkey"]
                            mypvc = inventive["senderencryptedkey"]
                            id = Database.add_chat(
                                name=f"{sender['id']}/{reciver['id']}",
                                user_ids=[int(sender["id"]), int(reciver["id"])],
                                type="p2p",
                                publickeycrypt=pbc
                            )
                            print(id)
                            chat={"type":"addmychat","chat":{"id":id["chat_id"],"type":"p2p","name":None,"photo":None,"about":None,"publickeycrypt":pbc,"privatekeycrypt":pvc,"myprivatekeycrypt":mypvc}}
                            await ws.send_json({"type":"addchat",
                                                "chat":{"id":id["chat_id"],
                                                        "type":"p2p",
                                                        "name":f"{sender['id']}/{reciver['id']}","photo":None,"about":None,
                                                        "publickeycrypt":pbc,"privatekeycrypt":pvc}})
                            await send_WS_msg(sender["email"],{"type":"addchat",
                                                               "chat":{"id":id["chat_id"],
                                                                       "type":"p2p",
                                                                       "name":f"{sender['id']}/{reciver['id']}","photo":None,"about":None,
                                                                       "publickeycrypt":pbc,
                                                                       "privatekeycrypt":mypvc}})
                            
                            Database.update_reciver_inventive(inventive["id"],chat_id=id["chat_id"])
                            break
                        if msg["type"]=="newchatdisagree":
                            print("disagree")
                            chats = filter(lambda x: x["type"] == "tehnic", Database.get_user_chats(sender["id"]))
                            for chat in chats:
                                Database.add_message(chat["id"],sender["id"],"txt",f"Пользователь {reciver['name']} отверг ваш запрос на создание чата с ним")   

                            Database.delete_Inventive(inventive["id"])
                            break

            if msg["type"]=="delchat":
                Database.delete_Chat(msg["id"])   
                participiants = Database.get_ChatParticipants(msg["id"])
                for p in participiants:
                    user = Database.get_user_by_id(int(p["id"]))
                    await send_WS_msg(user["email"],{"type":"deletechat","id":int(msg["id"])})


            if msg["type"]=="newmessage":
                ids=[]
                if msg["typemsg"]=="txt":
                    answ = Database.add_message(chat_id=int(msg["chatid"]),
                                                user_id=int(msg["userid"]),
                                                datatype=msg["typemsg"],
                                                content=json.dumps(msg["message"].replace("\'", "\"")))
                else:
                    msg["message"]=json.loads(msg["message"])
                    answ = Database.add_message(chat_id=int(msg["chatid"]),
                                                user_id=int(msg["userid"]),
                                                datatype=msg["typemsg"],
                                                content="")
                    if answ["success"]:
                        save_encrypted_media(msg["message"],answ["message_id"])
                        pathid=answ["message_id"]
                        answ1=Database.update_message(int(msg["chatid"]),int(answ["message_id"]),str(pathid),msg["typemsg"])
                        answ["success"]=answ1["success"]
                        print(344, answ, answ1)
                ids = 0
                if answ["success"]:
                    chat_ = Database.get_chat(int(msg["chatid"]))
                    m=""
                    match (chat_["type"]):
                            case "p2p":
                                chat_["photo"]=this_user["photo"]
                                if chat_["photo"] == None:
                                    chat_["photo"] = "/static/images/Uniknown.png"
                                chat_["name"]=this_user["name"]
                                m=f"{chat_['name']} отправил ....."
                                
                    print(chat_)
                    notify={
                            "title":chat_["name"],
                            "body":"new message" or m,
                            "avatar":chat_["photo"],
                            "chat_id":chat_["id"]
                                        }
                    await ws.send_json({"type":"addmymsg",
                                  "uniknownid":msg["uniknownid"],
                                  "message_id":answ["message_id"],
                                  "internal_id":answ["internal_id"],
                                  "typemsg":msg["typemsg"],
                                  "datatime": str(answ["time"]),
                                  "success":True})

                    for id in Database.get_ChatParticipants(chat_id=msg["chatid"]):
                        u = Database.get_user_by_id(id)
                        s=await send_WS_msg(u["email"],{"type":"addmsg",
                                    "message_id":answ["message_id"],
                                    "internal_id":answ["internal_id"],
                                    "chat_id": msg["chatid"],
                                    "user_id": msg["userid"],
                                    "typemsg": msg["typemsg"],
                                    "message": msg["message"],
                                    "datatime": str(answ["time"])
                                    },False,[str(this_deviceid)])
                        print(s)
                        if s["status"] == "offline":
                            if u["photo"] == None:
                                u["photo"]="/"
                            w=SendWEBpush(notify=notify,user_id=int(u["id"]),device_id="all")
                            print()
                 
                else:
                    await ws.send_json({"type":"addmymsg",
                                  "uniknownid":msg["uniknownid"],
                                  "success":False})
                    
            if msg["type"] == "Getnewlast":
                print(msg)
                if Database.get_user_by_id(msg["id"])["email"] == device_id.split("|id")[0] and device_id.split("|id")[1] != "newdevice":
                    MyLastIDs = msg["lastids"]
                    print(MyLastIDs)
                    for key in MyLastIDs:
                        key=key
                        my = MyLastIDs[key]["my"]
                        other = MyLastIDs[key]["other"]
                        m1= Database.get_max_msgid(key)
                        o1=Database.get_max_lastread(key,msg["id"])
                        print(o1)
                        if my < m1:
                            MyLastIDs[key]["my"]=m1
                        if other<=o1:
                            MyLastIDs[key]["other"]=o1

                    await ws.send_json({"type":"newlastdata",
                                        "lastdata":MyLastIDs})

            if msg["type"] == "reading":
                print(msg)
                fm=Database.get_max_lastread(msg["chat_id"],msg["user_id"])
                last_read_id = int(msg["last_read_id"])
                Database.update_lastread_participant(chat_id=int(msg["chat_id"]),participant_id=int(msg["user_id"]),lastread_id=last_read_id)
                sm=Database.get_max_lastread(msg["chat_id"],msg["user_id"])
                if sm>=fm:
                    for p in Database.get_ChatParticipants(msg["chat_id"]):
                        eml = Database.get_user_by_id(p["id"])["email"]
                        await send_WS_msg(eml,{"type":"newread","last_read_id":msg["last_read_id"],"chat_id":msg["chat_id"]},wait=False)

            if msg["type"] == "load_some_msg":
                msgs=Database.get_messages_more_less(msg["chat_id"],msg["id"],msg["limit"],True)
                await ws.send_json({"type":"old_msgs","msgs":msgs})
            
            if msg["type"] == "load_some_msg_new":
                msgs=Database.get_messages_more_less(msg["chat_id"],msg["id"],msg["limit"],False)
                await ws.send_json({"type":"new_msgs","msgs":msgs,"chat_id":msg["chat_id"]})

            if msg["type"] == "deletemsg":
                Database.delete_message(int(msg["id"]))
                Database.add_Event(msg["chat_id"],int(msg["id"]),"delete")
                for p in Database.get_ChatParticipants(msg["chat_id"]):
                    eml = Database.get_user_by_id(p["id"])["email"]
                    await send_WS_msg(eml,{"type":"delete_msg","id":int(msg["id"])},False,str([this_deviceid]))

            if msg["type"] == "get_msg_interval":
                print(474, msg)
                n_messages=Database.get_messages_interval(int(msg["chat_id"]) ,int(msg["min"]), int(msg["max"]))
                await ws.send_json({"type":"post_msg_interval","messages":n_messages,"chat_id":int(msg["chat_id"])})
            
            if msg["type"] == "call_client":
                p=Database.get_ChatParticipants(msg["chat_id"])
                if len(p)==2:
                    print(msg)
                    f=[False,-1]
                    for k in p:
                        if str(k["id"])==str(this_userid):
                            f[0]=True
                        else:f[1]=k["id"]
                    if f[0] and f[1]!= -1:
                        CurrentCallID = max(calls.keys())+1
                        calls[max(calls.keys())+1]=[device_id]
                        em=Database.get_user_by_id(int(f[1]))["email"]
                        r = await send_WS_msg(em,{"type":"call",
                                                  "user_id":f[1],
                                                  "chat_id":int(msg["chat_id"]),
                                                  "call_id":CurrentCallID},False)
                        
                        print(505,r)
                        await ws.send_json({"type":"call_answ","success":r["status"]=="sent","chat_id":int(msg["chat_id"]),"call_id":CurrentCallID})
                        if r["success"]==False:
                            del calls[CurrentCallID]
                    else:print(f)
                else:
                    del calls[CurrentCallID]
                    CurrentCallID = -1
                    await ws.send_json({"type":"call_answ","success":False})
                
            if msg["type"] == "accept_call":
                if calls.get(msg["call_id"]) is not None:
                    calls[msg["call_id"]].append(device_id)
                    for k in calls.get(msg["call_id"]):
                        if k!=device_id:
                            await send_WS_msg(k.split("|id")[0],{"type":"call_accepted"},False,[],[k.split("|id")[1]])  
              
                else:
                    await ws.send_json({"type":"kill_webrtc","call_id":msg["call_id"]})
                    CurrentCallID = -1
            
            if msg["type"] == "disaccept_call":
                CurrentCallID = -1     
                if calls.get(msg["call_id"]) is not None:
                    for k in calls.get(msg["call_id"]):
                        if k!=device_id:
                            print(k)
                            await send_WS_msg(k.split("|id")[0],{"type":"kill_webrtc","call_id":msg["call_id"]},False,[],[k.split("|id")[1]])  

            if msg["type"] == "answer" or msg["type"] == "offer" or msg["type"] == "ice":
                print(msg,calls)
                if calls.get(msg["call_id"]) is not None:
                    for k in calls.get(msg["call_id"]):
                        if k!=device_id:
                            await send_WS_msg(k.split("|id")[0],msg,False,[],[k.split("|id")[1]])  

            if msg["type"] == "subscription" and this_deviceid != "newdevice":
                Database.update_device(id=int(this_deviceid),subscription_data=msg["sub"])

            if msg["type"] == "get_last":
                print(msg)
                msgs=Database.get_messages_more_less(chat_id=int(msg["chat_id"]),after_id=Database.get_min_msgid(int(msg["chat_id"])),limit=15,reverse=False)

                msgs=Database.get_messages_more_less(int(msg["chat_id"]),Database.get_min_msgid(int(msg["chat_id"]))-1,15,False)
                await ws.send_json({"type":"new_msgs","msgs":msgs})

                
    except WebSocketDisconnect as wserror:
        try:
            print(f"[WS] Disconnected: {device_id}, {wserror.code}")
            if device_id.split("|id")[1]!="newdevice":
                WebSocketDevices.remove(device_id)
            clients.pop(device_id, None)
            for c in clients.get(this_email):
                if c["id"]==this_deviceid:
                    clients.get(this_email).remove(c)
            if len(clients.get(this_email)) == 0:
                clients.pop(this_email)
            if this_deviceid!="newdevice":
                Database.update_device(int(this_deviceid),last_seen=datetime.now())
            if CurrentCallID != -1:
                if calls.get(CurrentCallID) is not None:
                    for k in calls.get(CurrentCallID):
                        if k!=device_id:
                            await send_WS_msg(k.split("|id")[0],{"type":"kill_webrtc","call_id":CurrentCallID},False,[],[k.split("|id")[1]])
        except Exception as e:
            print(f"❌❌❌error removing {e, traceback.format_exc()}")
    except Exception as e:print(f"error work ws {e, traceback.format_exc()}")

#about:debugging#/runtime/this-firefox

# ПРОВЕРКА КОДА ЕМАИЛ 1 РЕГИСТРАЦИЯ
@app.post('/registrform')
async def getregistrblank(request:Request):
    data = await request.json()
    email=data.get("email").strip()
    if Database.get_user_by_email(email) is not None:
        return {"state":"youbeindb"}
    correct = IsEmailCorrect(email)
    if correct:
        state = SendCode(email)
        if type(state) == str:
            print(f"ERROR! {state}")
            return {"state":"errorpost"}
        if type(state) == list:
            if state[0]:
                DoctypeKeys[email]={"code":state[1],"attempents":3}
                print("ok email")
                return {"state":"ok"}
    else:
        print("errorfind email")
        return {"state":"errorfind"}

@app.post("/interkeydostype") # ПЕРВАЯ РЕГИСТРАЦИЯ
async def key(request:Request):
    data = await request.json()
    if data.get("key")==DoctypeKeys[data.get("email")]["code"]:
        print(f'adding user {data.get("name")} .........')
        del DoctypeKeys[data.get("email")]
        id=None
        res= Database.add_user(email=data.get("email"),
                        name=data.get("name"),
                        phone=data.get("phone"),
                        publickey=data.get("publickey"),
                        publickeycrypt=data.get("publickeycrypt")
                        )
        if res["success"]:
            print("success adding ///")
            dv =  Database.add_device(user_id=res["user_id"],
                                name=data.get("device"),
                                platform=data.get("platform"),
                                publickey=data.get("publickey"),
                                publickeycrypt=data.get("publickeycrypt"))
            if "device_id" in dv:
                device_id = dv["device_id"]
            else:
                return {"success":False,
                        "error":"db"}    
            user_id=res["user_id"]
            res= Database.add_chat(
                name="MIN поддержка",
                user_ids=[res["user_id"]],
                about="Технический чат",
                photo="static/images/logo.png"
            )
            if res["success"]:
                Database.add_message(
                    chat_id=res["chat_id"],
                    user_id=user_id,
                    datatype="txt",
                    content="успешно создан чат"
                )              
        else:
            return {"success":False,
                           "error":"db"}
        return {"success":True,
                        "user_id":user_id,
                        "device_id":device_id}
    else:
        DoctypeKeys[data.get("email")]["attempents"]-=1
        return {"success":False}

@app.post("/interkey2")
async def dostype_2(request:Request):
    data = await request.json()

    if data["email"] in DoctypeKeys:
        if DoctypeKeys[data["email"]]["attempents"]<1:
            del DoctypeKeys[data["email"]]
            Database.block_user(data["email"],hours=1)
            return {"success":"blocked"}
        if data["key"]==DoctypeKeys[data["email"]]["code"]:
            print("ok input")
            del DoctypeKeys[data["email"]]
            ip = request.client.host if request.client else "unknown"
            DevicesKeys[data["email"]]={"fingerprint":data["fingerprint"],"ip":ip}
            return {"success":True}
        else:
            print("errorinput")
            DoctypeKeys[data["email"]]["attempents"]-=1
            print(DoctypeKeys[data["email"]]["attempents"])
            if DoctypeKeys[data["email"]]["attempents"]<1:
                print("blocked user from")
                del DoctypeKeys[data["email"]]
                Database.block_user(data["email"],hours=1)
                return {"success":False}
            return {"success":False}
    else:
        return {"success":"error"}

@app.post("/doctypeinput")
async def eminp(request:Request):
    data = await request.json()
    email=data.get("email").strip()
    user=Database.get_user_by_email(email)
    if user is not None:
        if user["blocked"] is None or user["blocked"]<=datetime.now():
            state = SendCode(email)
            id = Database.get_user_by_email(email)["id"]
            chats = filter(lambda x: x["type"] == "tehnic", Database.get_user_chats(id))
            for chat in chats:
                a=Database.add_message(chat["id"], id ,"txt",f"код для входа в MIN {state[1]}")  
                if a["success"]:
                    await send_WS_msg(email,{"type":"addmsg",
                                    "message_id":a["message_id"],
                                    "internal_id":a["internal_id"],
                                    "chat_id": chat["id"],
                                    "user_id": 0,
                                    "typemsg": "txt",
                                    "message": f"код для входа в MIN {state[1]}",
                                    "datatime": str(datetime.now())
                                    })
            if type(state) == str:
                print(f"ERROR! {state}")
                return {"state":"errorpost"}
            if type(state) == list:
                if state[0]:
                    DoctypeKeys[email]={"code":state[1],"attempents":3}
                    print("ok email")
            return {"state":"ok"}
        else:
            tm=str(user["blocked"]-datetime.now()).split(":")[1]
            return {"state":"blocked",
                            "time":tm}
    else:
        print("errorfind email")
        return {"state":"errorfind"}

@app.post("/challenge")
async def challenge(request:Request):
    data = await request.json()
    user = Database.get_user_by_email(data["email"])
    if user is not None:
        challenge=os.urandom(32).hex()
        not_in = False
        if data["what"]["x"]=="auth":
            if data["email"] not in challenges_auth:
                challenges_auth[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
                not_in=True
        elif data["what"]["x"]=="del":
            if data["email"] not in challenges_del:
                challenges_del[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
                not_in=True
        elif data["what"]["x"]=="prof":
            if data["email"] not in challenges_prof:
                challenges_prof[data["email"]]={"challenge":challenge,"datatime": datetime.now()}  
                not_in=True
        elif data["what"]["x"]=="no_i_not" or data["what"]["x"]=="yes_i_my" :
            if data["email"] not in challenges_conn_device:
                challenges_conn_device[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
                not_in=True  
        elif data["what"]["x"]=="removedevice" :
            if data["email"] not in removedevicekeys:
                removedevicekeys[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
                not_in=True  
        else:
            print("uncorrect challenge format",not_in)
            return {"success":False,"wh":"unc"}
        return {"success":True, "challenge":challenge}
    else:
        print("user non")
        return {"success":False,"wh":"notdb"}

@app.post("/podpis")
async def podpis(request:Request):
    data = await request.json()
    email = data['email']
    challenge = data['challenge']
    signature = data['signature']

    all_stores = [challenges_auth, challenges_del, challenges_prof, challenges_conn_device, removedevicekeys]
    for store in all_stores:
        to_delete = []
        for email_2, data_2 in store.items():
            time_passed = datetime.now() - data_2["datatime"]
            if time_passed.total_seconds() > 25:
                to_delete.append(email_2)
        for email_2 in to_delete:
            del store[email_2]
    print("verify")
    try:
        match data["what"]["x"]:
            case "auth":
                if challenge!=challenges_auth[email]["challenge"]:
                    return {"success":False}
            case "del":
                if challenge!=challenges_del[email]["challenge"]:
                    return {"success":False}   
            case "prof":
                if challenge!=challenges_prof[email]["challenge"]:
                    return {"success":False}
            case "no_i_not":
                if challenge!=challenges_conn_device[email]["challenge"]:
                    return {"success":False}  
            case "yes_i_my":
                if challenge!=challenges_conn_device[email]["challenge"]:
                    return {"success":False} 
            case "removedevice":
                if challenge!=removedevicekeys[email]["challenge"]:
                    return {"success":False}            
    except:
        return {"success":False}
    match data["what"]['x']:
        case "auth": del challenges_auth[email]
        case "del": del challenges_del[email]
        case "prof": del challenges_prof[email]
        case "no_i_not": del challenges_conn_device[email]
        case "yes_i_my": del challenges_conn_device[email]
        case "removedevice": del removedevicekeys[email]
    user =  Database.get_user_by_email(email)
    if data["device"] not in [item['name'] for item in user["devices"]]:
        print(f"Device not in db ")
        return {"success":False}
    public_key_pem = list(filter(lambda x: x["publickey"] is not None, user["devices"]))[0]
    public_key_pem=public_key_pem["publickey"]

    is_valid = verify_signature_simple(challenge, signature, public_key_pem)
    print(is_valid,email)
    if is_valid:
        if data["what"]["x"]=="auth":
            print(f"success authorization {email}")
            WebSocketDevices.append(email+"|id"+str(data["device_id"]))
            return {"success":True}
                  
        if data["what"]["x"]=="del":
            if user["blocked"] is None or user["blocked"]<=datetime.now():
                if "why" in data["what"]:
                    feedbacksdb.add_userFeedBack(email,data["what"]["why"])
                try:
                    os.remove(user["photo"]) 
                except:pass
                Database.delete_User(user_email=email)
                print(f"Deleted user {email}")
                return {"success":True}
            print("blocked")
            return {"success":False,
                            "time":datetime.now()}
        if data["what"]["x"] == "prof":
            if user["blocked"] is None or user["blocked"]<=datetime.now():
                userdata=data["what"]["data"]
                path = save_photo_to_folder(user["id"],userdata["photo"])
                aboutme=""
                if userdata["age"] is not None:
                    aboutme+=f"Возраст: {userdata['age']}\n"
                if userdata["pol"] is not None:
                    aboutme+=f"Пол: {userdata['pol']}\n"
                if userdata["DR"] is not None:
                    aboutme+=f"день рождения: {userdata['DR']}\n"   
                if userdata["dopinf"] is not None:
                    aboutme+=f"Дополнительно: {userdata['dopinf']}\n"           
                if userdata["photo"] == None:
                    try:
                        os.remove(user["photo"]) 
                    except:pass
                Database.update_user(email=email,phone=userdata["phone"],name=userdata["name"],about=aboutme,photo=path)
                return {"success":True}
        if data["what"]["x"] == "no_i_not":
            
            try:
                if clients.get(data["email"]) is not None:
                    for c in clients.get(data["email"]):
                        if c["id"]=="newdevice":
                            await c["ws"].send_json({"type":"newdevice","success":False})
                            await c["ws"].close()
                            clients.get(data["email"]).remove(c)
                    return {"success":True,
                        "status": "sent"}

                return {"status": "error",
                                "success":False}
            except:    
                return {"status": "error",
                        "success":False}




        if data["what"]["x"] == "yes_i_my":
            print("agree on new device")
            success = False
            device_id = data["email"]+"|idnewdevice"
            print("Adding device.....")
            res = Database.add_device(user_id=user["id"],
                                name=data["what"]["device"],
                                publickey=None,
                                publickeycrypt=None,
                                platform=data["what"]["platform"])
            if "device_id" not in res:
                return {"success":False}
            id_dev = res["device_id"]
            if clients.get(data["email"]) is not None:
                for c in clients.get(data["email"]):
                    if c["id"]=="newdevice":
                        try:
                            await c["ws"].send_json({"type":"newdevice","success":True,"key":data["what"]["key"],"device_id":id_dev})
                            await c["ws"].close()
                            clients.get(data["email"]).remove(c)
                            success = True
                        except:
                            Database.delete_Device(id_dev)
                            success = False
            else:
                return {"status": False,
                            "success":False}

            
            return {"success":success}




        if data["what"]["x"] == "removedevice":
            devices = Database.get_user_devices(int(data["id"]))
            print("devices",devices)
            if len(devices)<2:
                return {"success":True,"answ":"no"}
            else:
                Database.delete_Device(int(data["device_id"]))
                return {"success":True,"answ":"yes"}

                            

    else:
        print("false podpis")
        message=0
        tm=0
        match data["what"]["x"]:
            case "auth":
                tm=6
                message="""
Кто-то пытается войти в ваш аккаунт,
                  попытка входа в аккаунт или его удаление будут заблокированы на 6 часов!
"""
            case "del":
                tm=3
                message="""
Кто-то пытается удалить ваш аккаунт,
                  попытка входа в аккаунт или его удаление будут заблокированы на 3 часа!
"""
            case "prof":
                tm=2
                message="""
Кто-то пытается изменить ваш профиль,
                  попытка редакции профиля, входа в аккаунт или его удаление будут заблокированы на 2 часа!
"""
        if message!=0:
            SendCode(email,message)
            Database.block_user(email,tm)
        return {"success":False}  

@app.post("/userchatlist")
async def returnUserChatList(request:Request):
    data = await request.json()
    if "id" not in data:
        return []
    id = data["id"]
    chats = Database.get_user_chats(id)
    if chats is not None:
        return chats
    return []

@app.post("/SearchUserBy")
async def SearchUserBy(request:Request):
    data = await request.json()
    print(data)
    typeS = data["type"]
    what = data["request"]
    back = {"sucess":True, "userlist":[]}
    res = Database.search_users_by(what,typeS)
    print(res)
    back["sucess"]=len(res)>0 
    if back["sucess"]:
        back["userlist"]=[{"id":i['id'],"name":i['name'],"photo":i["photo"],"publickeycrypt": list(filter(lambda x: x["publickeycrypt"] is not None, i["devices"]))[0]["publickeycrypt"]} for i in res]
    return back

@app.post("/GetUserInfo")
async def GetUserInfo(request:Request):
    data = await request.json()
    print(data)
    if 'id' in data:
        user = Database.get_user_by_id(data["id"])
    else:
        user = Database.get_user_by_email(data["email"])
    
    dt = {"userid":user['id'],
                    "email":user['email'],
                    "name":user['name'],
                    "photo":user["photo"],
                    "phone":user['phone'],
                    "publickeys":{"publickey":user["publickey"],"publickeycrypt":user["publickeycrypt"]}}
    if user["about"]!=None:
        for d in user["about"].split("\n"):
            if len(d.split(":")) == 2:
                if d.split(":")[0] == "Возраст":
                    dt["age"]=d.split(":")[1].strip()
                if d.split(":")[0] == "Пол":
                    dt["pol"]=d.split(":")[1].strip()
                if d.split(":")[0] == "день рождения":
                    dt["DR"]=d.split(":")[1]
                if d.split(":")[0] == "Дополнительно":
                    dt["about"]=d.split(":")[1]
    return dt

@app.post("/push")
async def Wss_Push_Notify(request:Request):
    data = await request.json()
    ip = request.client.host if request.client else "unknown"
    if data["type"] == "newdevice":
        if data["email"] in DevicesKeys:
            if ip==str(DevicesKeys[data["email"]]["ip"]) and DevicesKeys[data["email"]]["fingerprint"] == data["fingerprint"]:
                DevicesKeys[data["email"]]={"publickey":data["publickey"],"fingerprint":data["fingerprint"],"device":data["device"],"status":"waiting"}
                data["ip"]=ip
                res=await send_WS_msg(data["email"],data,True)
                return res
            else:
                print("bigauth")
        else:
            print("not in devicekeys")
    else:
        print("error632")        
    print("returning")
    return {"success":"error"}

@app.post("/cancel")
async def cancel(request: Request):
    data = await request.json()
    print(request.client.host)
    try:
        if clients.get(data["email"]) is not None:
            for c in clients.get(data["email"]):
                if c["id"]=="newdevice":
                    await c["ws"].close()
                    clients.get(data["email"]).remove(c)
            return {"success":True,
                "status": "sent"}

        return {"status": "error",
                        "success":False}
    except:    
        return {"status": "error",
                "success":False}


@app.post("/GetUs")
async def getus(request: Request):
    data = await request.json()
    try:
        us = Database.get_user_by_id(int(data["id"]))
        if us==None:
            return {}
    except:
        return {}
    if data["photo"]:
        return {"name":us["name"],"photo":us["photo"]}
    else:
        return {"name":us["name"]}    

@app.post("/CancelAuthNewDevice")
async def getus(request: Request):
    data = await request.json()

@app.get("/push_key")
async def push_key():
    return {"key": PUBLIC_KEY}

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