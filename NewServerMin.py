from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
import MainUsersDB
import FeedBacks
import os
import smtplib
import random
import json
import base64  
import uuid

with open('static\images\logo.png', 'rb') as img:  
    minb=base64.b64encode(img.read()).decode('utf-8')

simv="qwertyuioplkjhgfdsazxcvbnm@#_1234567890"



DoctypeKeys={}
DevicesKeys = {}
challenges_auth={}
challenges_del={}
challenges_prof={}
challenges_conn_device={}

feedbacksdb = FeedBacks.Feedback_Manager()
usersdb = MainUsersDB.UserManager()


app = Flask(__name__)
CORS(app)



def save_photo_to_folder(name, photo_base64):
    """
    Сохраняет base64 фото в папку на сервере
    
    Args:
        email: email пользователя (для имени файла)
        photo_base64: строка base64 (может быть с префиксом data:image/... или без)
    
    Returns:
        str: имя сохраненного файла или None при ошибке
    """
    try:
        # Проверяем что фото есть
        if not photo_base64:
            print("❌ Нет данных фото")
            return None
        
        # Убираем префикс "data:image/jpeg;base64," если есть
        if ',' in photo_base64:
            photo_base64 = photo_base64.split(',')[1]
        
        # Декодируем base64 в bytes
        photo_bytes = base64.b64decode(photo_base64)
        
        # Создаем папку если не существует
        upload_folder = 'UsersPhotos'
        os.makedirs(upload_folder, exist_ok=True)
        
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{name}_{timestamp}_{unique_id}.jpg"
        filepath = f"{upload_folder}/{filename}"
        
        # Сохраняем файл
        with open(filepath, 'wb') as f:
            f.write(photo_bytes)
        print(f"✅ Фото сохранено: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ Ошибка сохранения фото: {e}")
        return None


def verify_signature_simple(challenge, signature_b64, public_key_data):
    """
    Улучшенная проверка подписи
    
    challenge: строка которую подписывали (например: "abc123")
    signature_b64: подпись в base64
    public_key_data: публичный ключ в PEM формате ИЛИ голый base64
    """
    try:
        # 1. Декодируем подпись из base64
        signature_bytes = base64.b64decode(signature_b64)
        
        # 2. Обрабатываем публичный ключ (может быть PEM или голым base64)
        public_key_pem = public_key_data.strip()
        
        # Если это не PEM, добавляем заголовки
        if not public_key_pem.startswith('-----BEGIN'):
            # Декодируем base64 и создаем PEM
            public_key_bytes = base64.b64decode(public_key_pem)
            public_key_pem = f"""-----BEGIN PUBLIC KEY-----
{base64.b64encode(public_key_bytes).decode('utf-8')}
-----END PUBLIC KEY-----"""
        
        # 3. Загружаем публичный ключ
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        
        # 4. Проверяем подпись
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



@app.route("/")
def index():
    return render_template("RegisterUser.html")

@app.route("/messenger.html")
def index3():
    return render_template("messenger.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/static/js/sw.js')
def send_swjs():
    with open("static\js\sw.js","r+",encoding="utf-8") as f:
        js = f.read()
    return Response(js, mimetype="application/javascript")


@app.route('/UsersPhotos/<path:path>')
def send_userphoto(path):
    return send_from_directory('UsersPhotos', path)

@app.route('/static/js/<path:path>')
def send_JavaScript(path):
    return send_from_directory('static/js', path)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'logo.png' \
                               '', mimetype='image/vnd.microsoft.icon')


#####################################################
#####################################################
#####################################################
#####################################################
#####################################################

@app.route('/registrform',methods=["POST"])# ПРОВЕРКА КОДА ЕМАИЛ 1 РЕГИСТРАЦИЯ
def getregistrblank():
    data = request.get_json()
    email=data["email"].strip()
    if len(usersdb.get_user_by_email(email))>0:
        return jsonify({"state":"youbeindb"})
    correct = IsEmailCorrect(email)
    #return jsonify({"state":"ok"})
    if correct:
        state = SendCode(email)
        if type(state) == str:
            print(f"ERROR! {state}")
            return jsonify({"state":"errorpost"})
        if type(state) == list:
            if state[0]:
                DoctypeKeys[email]={"code":state[1],"attempents":3}
                print("ok email")
                return jsonify({"state":"ok"})
    else:
        print("errorfind email")
        return jsonify({"state":"errorfind"})
            
@app.route("/interkeydostype",methods=["POST"]) # ПЕРВАЯ РЕГИСТРАЦИЯ
def key():
    data = request.get_json()
    if data["key"]==DoctypeKeys[data["email"]]["code"]:
        print(f'adding user {data["name"]} .........')
        d={data["device"]:{"publickey":data["publickey"],"publickeycrypt":data["publickeycrypt"]}}
        usersdb.add_user(email=data["email"], userid=usersdb.get_max_userid()["id"]+1, name=data["name"], phone=data["phone"], devices=str(d))  
        del DoctypeKeys[data["email"]]
        return jsonify({"success":True})
    else:
        DoctypeKeys[data["email"]]["attempents"]-=1
        return jsonify({"success":False})

@app.route("/interkey2", methods=["POST"])
def dostype_2():
    data = request.get_json()

    if data["email"] in DoctypeKeys:
        if DoctypeKeys[data["email"]]["attempents"]<1:
            del DoctypeKeys[data["email"]]
            usersdb.block_user(data["email"],hours=1)
            return jsonify({"success":"blocked"})
        if data["key"]==DoctypeKeys[data["email"]]["code"]:
            print("ok input")
            del DoctypeKeys[data["email"]]
            ip = request.environ['REMOTE_ADDR']
            DevicesKeys[data["email"]]={"fingerprint":data["fingerprint"],
                                        "ip":ip}
            return jsonify({"success":True})
        else:
            print("errorinput")
            DoctypeKeys[data["email"]]["attempents"]-=1
            print(DoctypeKeys[data["email"]]["attempents"])
            if DoctypeKeys[data["email"]]["attempents"]<1:
                print("blocked user from")
                del DoctypeKeys[data["email"]]
                usersdb.block_user(data["email"],hours=1)
                return jsonify({"success":False})
            return jsonify({"success":False})      
    else:
        return jsonify({"success":"error"})


@app.route("/challenge", methods=["POST"])
def challenge():
    data=request.get_json()
    user=usersdb.get_user_by_email(data["email"])
    if len(user) > 0:
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
        else:
            return jsonify({"success":False}) 
        return jsonify({"success":True, "challenge":challenge}) 
    else:
        return jsonify({"success":False}) 

@app.route("/podpis", methods=["POST"])
def podpis():
    data=request.get_json()
    email = data['email']
    challenge = data['challenge']
    signature = data['signature']

    all_stores = [challenges_auth, challenges_del, challenges_prof, challenges_conn_device]
    for store in all_stores:
        to_delete = []
        for email_2, data_2 in store.items():
            time_passed = datetime.now() - data_2["datatime"]
            if time_passed.total_seconds() > 25:
                to_delete.append(email_2)
        for email_2 in to_delete:
            del store[email_2]
    try:
        match data["what"]["x"]:
            case "auth":
                if challenge!=challenges_auth[email]["challenge"]:
                    return jsonify({"success":False})    
            case "del":
                if challenge!=challenges_del[email]["challenge"]:
                    return jsonify({"success":False})    
            case "prof":
                if challenge!=challenges_prof[email]["challenge"]:
                    return jsonify({"success":False})    
            case "no_i_not":
                if challenge!=challenges_conn_device[email]["challenge"]:
                    return jsonify({"success":False})    
            case "yes_i_my":
                if challenge!=challenges_conn_device[email]["challenge"]:
                    return jsonify({"success":False})    
    except:
        return jsonify({"success":False})    
    match data["what"]['x']:
        case "auth": del challenges_auth[email]
        case "del": del challenges_del[email]
        case "prof": del challenges_prof[email]
        case "no_i_not": del challenges_conn_device[email]
        case "yes_i_my": del challenges_conn_device[email]
    user = usersdb.get_user_by_email(email)
    print(data,user)
    if data["device"] not in user["devices"]:
        print("Device not in db")
        return jsonify({"success":False})  
    public_key_pem = user["devices"][next(iter(user["devices"]))]
    public_key_pem=public_key_pem["publickey"]
    is_valid = verify_signature_simple(challenge, signature, public_key_pem)
    if is_valid:
        if data["what"]["x"]=="auth":
            print(f"success authorization {email}")
            return jsonify({"success":True})
                  
        if data["what"]["x"]=="del":
            if user["blocked"] is None or user["blocked"]<=datetime.now():
                if "why" in data["what"]:
                    feedbacksdb.add_userFeedBack(email,data["what"]["why"])
                try:
                    os.remove(usersdb.get_user_by_email(email)["photo"]) 
                except:pass
                usersdb.delete_user(email)
                print(f"Deleted user {email}")
                return jsonify({"success":True})
            print("blocked")
            return jsonify({"success":False,
                            "time":datetime.now()})
        if data["what"]["x"] == "prof":
            if user["blocked"] is None or user["blocked"]<=datetime.now():
                userdata=data["what"]["data"]
                path = save_photo_to_folder(user["userid"],userdata["photo"])
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
                usersdb.update_user(email=email,phone=userdata["phone"],name=userdata["name"],about=aboutme,photo=path)
                return jsonify({"success":True})
        if data["what"]["x"] == "no_i_not":
            r = requests.post("https://127.0.0.1:8000/cancel_agree",json={"email":email+'newdevice'},verify=False)
            return jsonify({"success":True})
        if data["what"]["x"] == "yes_i_my":
            
            r = requests.post("https://127.0.0.1:8000/i_agree",json={"email":email+'newdevice',"key":data["what"]["key"]},verify=False)
            if r.json()["success"]==True:
                print("Adding device.....")
                usersdb.add_device(email,data["what"]["device"],{})
                return jsonify({"success":True})
            else:return jsonify({"success":False})
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
            usersdb.block_user(email,tm)
        return jsonify({"success":False})        
        




@app.route("/doctypeinput",methods=["POST"])
def eminp():
    email=request.get_json()["email"].strip()
    user=usersdb.get_user_by_email(email)
    if len(user)>0:
        if user["blocked"] is None or user["blocked"]<=datetime.now():
            state = SendCode(email)
            if type(state) == str:
                print(f"ERROR! {state}")
                return jsonify({"state":"errorpost"})
            if type(state) == list:
                if state[0]:
                    DoctypeKeys[email]={"code":state[1],"attempents":3}
                    print("ok email")
            return jsonify({"state":"ok"})
        else:
            tm=str(user["blocked"]-datetime.now()).split(":")[1]
            return jsonify({"state":"blocked",
                            "time":tm})
    else:
        print("errorfind email")
        return jsonify({"state":"errorfind"})


#################################################
#################################################
#################################################

@app.route("/userchatlist",methods=["POST"])
def returnUserChatList():
    email = request.get_json()["email"]
    chats=list(usersdb.get_user_by_email(email)["chats"])
    if len(chats)!=0:
        print("yes")
        return jsonify({"chats":json.loads(chats)})
    else:
        return jsonify({"chats":[{"avatar":'\static\images\logo.png',"name":'MIN-поддержка'}, {"avatar":None,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'russia'},{"avatar":0b0,"name":'polyaki'}]})


@app.route("/SearchUserBy",methods=["POST"])
def SearchUserBy():
    data = request.get_json()
    typeS = data["type"]
    what = data["request"]
    back = {"sucess":True, "userlist":[]}
    res=usersdb.search_users_by(what,typeS)
    back["sucess"]=len(res)>0
    back["userlist"]=[{"id":i['userid'],"name":i['name'],"photo":i["photo"]} for i in res]
    return jsonify(back)

@app.route("/GetUserInfo",methods=["POST"])
def GetUserInfo():
    data = request.get_json()
    if 'id' in data:
        user=usersdb.get_user_by_id(data["id"])
    else:
        user=usersdb.get_user_by_email(data["email"])
    

    dt = {"id":user['userid'],
                    "email":user['email'],
                    "name":user['name'],
                    "photo":user["photo"],
                    "phone":user['phone'],
                    "publickeys":user["devices"][next(iter(user["devices"]))]}
    print(dt)
    if user["about"]!=None:
        print(user["about"].split("\n"))
        for d in user["about"].split("\n"):
            if len(d.split(":")) == 2:
                if d.split(":")[0] == "Возраст":
                    dt["age"]=int(d.split(":")[1].strip())
                if d.split(":")[0] == "Пол":
                    dt["pol"]=d.split(":")[1].strip()
                if d.split(":")[0] == "день рождения":
                    dt["DR"]=d.split(":")[1]
                if d.split(":")[0] == "Дополнительно":
                    dt["about"]=d.split(":")[1]
    return jsonify(dt)



@app.post("/push")
def Wss_Push_Notify():
    data = request.get_json()
    ip = request.environ['REMOTE_ADDR']
    print(data,DevicesKeys)
    if data["type"] == "newdevice":
        if data["email"] in DevicesKeys:
            if ip==str(DevicesKeys[data["email"]]["ip"]) and DevicesKeys[data["email"]]["fingerprint"] == data["fingerprint"]:
                DevicesKeys[data["email"]]={"publickey":data["publickey"],"fingerprint":data["fingerprint"],"device":data["device"],"status":"waiting"}
                data["ip"]=ip
                r = requests.post("https://127.0.0.1:8000/notify",json=data,verify=False)
                print("❌ ",r.json())
                return jsonify(r.json())
    return jsonify({"success":"error"})


@app.route("/CancelAuthNewDevice",methods=["POST"])
def CancelNewDevice():
    data=request.get_json()
    ip = request.environ['REMOTE_ADDR']   
    if data["type"] == "newdevice":
        if data["email"] in DevicesKeys:
            print(DevicesKeys)
            if DevicesKeys[data["email"]]["fingerprint"] == data["fingerprint"]:
                r = requests.post("https://127.0.0.1:8000/cancel",json=data,verify=False)
                print(r)
    return jsonify({})





if __name__ == '__main__':    
    app.run( host='0.0.0.0',  port=5000, debug=True, 
            ssl_context=('cert.pem',"key.pem"),
            use_reloader=False) 