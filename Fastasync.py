from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import smtplib
import json
import random
import MessengerDataBase
import FeedBacks
import uvicorn
import base64, uuid
import os, sys, traceback

clients = {}
wait_for = {}
WebSocketDevices=[]
DoctypeKeys={}
DevicesKeys = {}
removedevicekeys={}
challenges_auth={}
challenges_del={}
challenges_prof={}
challenges_conn_device={}

app = FastAPI()
Database = MessengerDataBase.DataBaseManager()
feedbacksdb = FeedBacks.Feedback_Manager()
templates = Jinja2Templates(directory="templates")


def save_encrypted_media(payload: dict) -> str:
    media_id = str(uuid.uuid4())

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

def SendCode(emailreciver,body=0):
    email_from = 'onesevenrusia@gmail.com' 
    password = 'qhxw zqci vqit xwvp'  
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

@app.get('/favicon.ico')
def favicon():
    return FileResponse('static/images/logo.png')

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
#

async def send_WS_msg(reciver, msg):
    flag=False
    for client in filter(lambda x: reciver in x and reciver+"|idnewdevice" not in x, clients):
        try:
            client = clients[client]
            await client["ws"].send_json(msg)
            flag=True
        except Exception as e:
            print(e)
            return {"status": "error",
                    "success":False}
    if not flag:
        if reciver not in wait_for:
            wait_for[reciver]=[]
        wait_for[reciver].append(msg)  
        return {
            "success":True,
            "status": "offline"
            }
    else:            
        return {"success":True,
                    "status": "sent"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket): 
    await ws.accept()
    device_id = ws.query_params.get("device_id")
    if not device_id:
        await ws.close()
        return
    if "newdevice" in device_id:
        if device_id.split("|id")[0] not in DevicesKeys or device_id in clients:
            await ws.close()
            return     
    else:
        if device_id not in WebSocketDevices or device_id in clients:
            print("not in devices/clients",WebSocketDevices,clients,device_id)
            await ws.close()
            return     
    

    print(f"[WS] Connected: {device_id}")
    clients[device_id] = {"ws":ws}
    try:
        if device_id.split("|")[0] in wait_for:
            for message in wait_for[device_id.split("|")[0]]:
                await clients[device_id]["ws"].send_json(message)
                wait_for[device_id].remove(message)
        #print(f'#{Database.get_user_Inventives(device_id.split("|")[0])}#')
        for inventive in Database.get_user_Inventives(device_id.split("|")[0]):
            inventive["time"]=inventive["time"].isoformat()
            if inventive["typeinventive"]=="newchat":
                await clients[device_id]["ws"].send_json({"type":"new_chat","user":inventive["emailsent"],"time":inventive["time"],"publickey":inventive["publickey"],"privatekey":inventive["reciverencryptedkey"]})
    except Exception as e:
        print(e)
    try:
        while True:
            msg = await ws.receive_json()
            print(f"[WS] From {device_id}: {msg}")
            if msg["type"] == "newchat":
                if "newdevice" not in device_id and msg["email"] not in device_id:
                    for client in filter(lambda x: msg["email"] in x and msg["email"]+"|idnewdevice" not in x, clients):
                        try:
                            client = clients[client]
                            await client["ws"].send_json({"type":"new_chat","user":device_id.split("|")[0]})
                        except Exception as e:
                            print("248❌",e)
                    Database.add_Inventive(emailrecive=msg["email"],
                                               emailsent=device_id.split("|")[0],
                                               inventivetype="newchat",
                                               publickey=msg["publickey"],
                                               message=None,
                                               reciverencryptedkey=str(msg["encrypted"]),
                                               senderencryptedkey=str(msg["myencrypted"])
                                            )
                    await ws.send_json({"type":"answnewchat","success":"waiting"})
                else:
                    try:
                        await ws.send_json({"type":"answnewchat","success":"error"})
                    except Exception as e:              
                        print("262❌",e)
            if msg["type"] == "newchatagree" or msg["type"] == "newchatdisagree":
                print(f"[Agree] {msg}")
                sender = Database.get_user_by_email(msg["email"])
                reciver = Database.get_user_by_email(device_id.split("|")[0])
                for inventive in Database.get_user_Inventives(reciver["email"]):
                    if inventive["emailsent"]==msg["email"] and inventive["typeinventive"]=="newchat":
                        if msg["type"]=="newchatagree":
                            print("agree")
                            print(inventive)
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
                            Database.delete_Inventive(inventive["id"])
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

            if msg["type"]=="newmessage":
                if msg["typemsg"]=="txt":
                    answ = Database.add_message(chat_id=int(msg["chatid"]),
                                                user_id=int(msg["userid"]),
                                                datatype=msg["typemsg"],
                                                content=json.dumps(msg["message"].replace("\'", "\"")))
                else:
                    r=save_encrypted_media(msg["message"])
                    print(r)
                if answ["success"]:
                    await ws.send_json({"type":"addmymsg",
                                  "uniknownid":msg["uniknownid"],
                                  "message_id":answ["message_id"],
                                  "internal_id":answ["internal_id"],
                                  "datatime": str(answ["time"]),
                                  "success":True})
                    emails=[]
                    for id in Database.get_ChatParticipants(chat_id=msg["chatid"]):
                        email = Database.get_user_by_id(id)["email"]
                        emails.append(email)
                    #print(clients)
                    for client in clients:
                        print(client.split("|id")[0] , emails)
                        if client.split("|id")[0] in emails and client.split("|id")[1] != "newdevice" and device_id.split("|")[0] not in client:
                            print("sending to ...")
                            try:
                                await clients[client]["ws"].send_json({"type":"addmsg",
                                    "message_id":answ["message_id"],
                                    "internal_id":answ["internal_id"],
                                    "chat_id": msg["chatid"],
                                    "user_id": msg["userid"],
                                    "typemsg": msg["typemsg"],
                                    "message": msg["message"],
                                    "datatime": str(answ["time"])
                                    })
                            except Exception as e:print("337❌ ",e,traceback.format_exc())
                else:
                    await ws.send_json({"type":"addmymsg",
                                  "uniknownid":msg["uniknownid"],
                                  "success":False})
            if msg["type"] == "GetUnreadMsg":
                if Database.get_user_by_id(msg["id"])["email"] == device_id.split("|id")[0] and device_id.split("|id")[1] != "newdevice":
                    unread = Database.getALL_unread_messages(msg["id"])
                    if len(unread)>0:
                        await ws.send_json({"type":"newunread","messages":unread})

                
    except WebSocketDisconnect as wserror:
        try:
            print(f"[WS] Disconnected: {device_id}, {wserror.code}")
            if device_id.split("|id")[1]!="newdevice":
                WebSocketDevices.remove(device_id)
            clients.pop(device_id, None)
        except Exception as e:
            print(f"❌❌❌error removing {e}")
    except Exception as e:print(f"error work ws {e, traceback.format_exc()}")

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
        if data["what"]["x"]=="auth":
            if data["email"] not in challenges_auth:
                challenges_auth[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
        elif data["what"]["x"]=="del":
            if data["email"] not in challenges_del:
                challenges_del[data["email"]]={"challenge":challenge,"datatime": datetime.now()}
        elif data["what"]["x"]=="prof":
            if data["email"] not in challenges_prof:
                challenges_prof[data["email"]]={"challenge":challenge,"datatime": datetime.now()}  
        elif data["what"]["x"]=="no_i_not" or data["what"]["x"]=="yes_i_my" :
            if data["email"] not in challenges_conn_device:
                challenges_conn_device[data["email"]]={"challenge":challenge,"datatime": datetime.now()}        
        elif data["what"]["x"]=="removedevice" :
            if data["email"] not in removedevicekeys:
                removedevicekeys[data["email"]]={"challenge":challenge,"datatime": datetime.now()}        
        else:
            return {"success":False}
        return {"success":True, "challenge":challenge}
    else:
        return {"success":False}

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
                Database.delete_user(email=email)
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
            device_id = data["email"]+"|idnewdevice"
            if device_id in clients:
                try:
                    await clients[device_id]["ws"].send_json({"type":"new_device","success":False})
                    clients[device_id]["ws"].close()
                    del clients[device_id]
                except:
                    pass
            else:
                if device_id not in wait_for:
                    wait_for[device_id]=[]
                wait_for[device_id].append({"type":"new_device","success":False})     
            return {"success":True}

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
            if device_id in clients:
                try:
                    await clients[device_id]["ws"].send_json({"type":"new_device","success":True,"key":data["what"]["key"],"device_id":id_dev})
                    del clients[device_id]
                    success = True
                except:
                    Database.delete_Device(id_dev)
                    success = False
            else:
                if device_id not in wait_for:
                    wait_for[device_id]=[]
                wait_for[device_id].append({"type":"new_device","success":True,"key":data["what"]["key"], "device_id":id_dev})        
                success = True

            return {"success":success}

        if data["what"]["x"] == "removedevice":
            dname=data["device"]
            devices = Database.get_user_devices(data["id"])
            print("devices",devices)
            if len(devices)<2:
                return {"success":True,"answ":"no"}
            else:
                flaf=False
                for d in devices:
                    if d["name"]==dname:
                        if d["publickey"] is not None:
                            id1=d["id"]
                            pbk=d["publickey"]
                            pbkcrypt=d["publickeycrypt"]
                            flaf=True
                            break
                if flaf:
                    for d2 in devices:
                        if d2["publickey"] is None:
                            if Database.update_device(id=d2["id"],publickey=pbk,publickeycrypt=pbkcrypt)["success"]:
                                Database.delete_Device(id1)
                                return {"success":True,"answ":"yes"}
                            else:break
                return {"success":True,"answ":"no"}
                            

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
                    "publickeys":{"publickey":user["devices"][0]["publickey"],"publickeycrypt":user["devices"][0]["publickeycrypt"]}}
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
                dv = Database.get_user_by_email(data["email"])["devices"]
                for d in dv:
                    device_id = data["email"]+"|id"+str(d["id"])
                    if device_id in clients:
                        try:
                            print("sending")
                            await clients[device_id]["ws"].send_json(data)
                            return {"success":True,
                                    "status": "sent"}
                        except:
                            print("error send")
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
    device_id = data["email"]+"}idnewdevice"
    if device_id in clients:
        try:
            if device_id in clients:
                for m in clients[device_id]["msgoffline"]:
                    if m["type"]=="newdevice":
                        clients[device_id]["msgoffline"].pop(m ,None)

            await clients[device_id+'}idnewdevice']["ws"].close()
            return {"success":True,
                    "status": "sent"}
        except:pass
    return {"status": "error",
                    "success":False}
@app.post("/GetUs")
async def getus(request: Request):
    data = await request.json()
    try:
        us = Database.get_user_by_id(data["id"])
    except:
        return {}
    if data["photo"]:
        return {"name":us["name"],"photo":us["photo"]}
    else:
        return {"name":us["name"]}    


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem"
    )