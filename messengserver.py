from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from email_validator import validate_email, EmailNotValidError
import SearchUser
import json

import base64  
with open('static\images\logo.png', 'rb') as img:  
    minb=base64.b64encode(img.read()).decode('utf-8')

simv="qwertyuioplkjhgfdsazxcvbnm@#_1234567890"

DoctypeKeys={}
usersdb = SearchUser.UserManager()


app = Flask(__name__)
CORS(app)

def IsEmailCorrect(email):
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError:
        return False

def SendCode(emailreciver):
    email_from = 'onesevenrusia@gmail.com' 
    password = 'qhxw zqci vqit xwvp'  
    email_to = emailreciver
    code=str(random.randint(100000, 999999))
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = 'Ваш код подтверждения'
    body = f"""
    Здравствуйте!
    Ваш код для подтверждения: <b>{code}</b>

    Никому не сообщайте этот код.
    """
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
    return render_template("index.html")

@app.route("/messenger.html")
def index3():
    return render_template("messenger.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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

@app.route('/registrform',methods=["POST"])
def getregistrblank():
    data = request.get_json()
    email=data["email"]
    correct = IsEmailCorrect(email)
    #return jsonify({"state":"ok"})
    if correct:
        state = SendCode(email)
        if type(state) == str:
            print(f"ERROR! {state}")
            return jsonify({"state":"errorpost"})
        if type(state) == list:
            if state[0]:
                DoctypeKeys[email]=state[1]
                print("ok email")
                return jsonify({"state":"ok"})
    else:
        print("errorfind email")
        return jsonify({"state":"errorfind"})
            
@app.route("/interkeydostype",methods=["POST"])
def key():
    data = request.get_json()
    print(data,DoctypeKeys)
    print(data["key"]==DoctypeKeys[data["email"]])
    if data["key"]==DoctypeKeys[data["email"]]:
        token=[]
        for i in range(random.randint(27,35)):
            if random.randint(0,1) == 1:
                token.append(simv[random.randint(0,len(simv)-1)].upper())
            else:
                token.append(simv[random.randint(0,len(simv)-1)])
        token=str("".join(token))     
        print("adding user to", data)   
        usersdb.add_user(email=data["email"], userid=usersdb.get_max_userid()["id"]+1, name=data["name"], phone=data["phone"], token=token)  
        print(usersdb.get_user_by_email(data["email"])) 
        #usersdb.adduser(email=data["email"], name=data["name"], phone=data["phone"], token=token)
        return jsonify({"success":True,
                        "token":token})
    else:
        return jsonify({"success":False})

@app.route("/input", methods=["POST"])
def input():
    data=request.get_json()
    #token=usersdb.getUser(data["email"], ["token"])
    token = usersdb.get_user_by_email(data["email"])
    if len(token)>0:
        token=token["token"]
    else:
        return jsonify({"state":False})        
    try:
        print(token,data["token"])
        if token[0] == data["token"].replace(" ",""):
            print("ok input")
            return jsonify({"state":True})
        else:
            return jsonify({"state":False})
    except:
        return jsonify({"state":False})

@app.route("/doctypeinput",methods=["POST"])
def eminp():
    email=request.get_json()["email"]
    fl=False
    for user in usersdb.get_all_users():
        if email == user["email"]:
            fl=True
            break
    if fl:
        state = SendCode(email)
        if type(state) == str:
            print(f"ERROR! {state}")
            return jsonify({"state":"errorpost"})
        if type(state) == list:
            if state[0]:
                DoctypeKeys[email]=state[1]
                print("ok email")
        return jsonify({"state":"ok"})
    else:
        print("errorfind email")
        return jsonify({"state":"errorfind"})

@app.route("/interkey2", methods=["POST"])
def dostype_2():
    data = request.get_json()
    print(DoctypeKeys)
    print(data, "z")
    if data["key"]==DoctypeKeys[data["email"]]:
        #print(usersdb.getUser(data["email"],["token"]))
        print("ok input")
        return jsonify({"success":True,
                        "token":usersdb.get_user_by_email(data["email"])["token"]})
    
    else:
        print("errorinput")
        return jsonify({"success":False})      

#################################################
#################################################
#################################################

@app.route("/userchatlist",methods=["POST"])
def returnUserChatList():
    email = request.get_json()["email"]
    print("email",usersdb.get_user_by_email(email))
    chats=list(usersdb.get_user_by_email(email)["chats"])
    print(chats)
    if len(chats)!=0:
        print("yes")
        return jsonify({"chats":json.loads(chats)})
    else:
        return jsonify({"chats":[{"avatar":'\static\images\logo.png',"name":'MIN-поддержка'}, {"avatar":0b0,"name":'123abcname'},{"avatar":0b0,"name":'russia'},{"avatar":0b0,"name":'polyaki'}]})


@app.route("/SearchUserBy",methods=["POST"])
def SearchUserBy():
    data = request.get_json()
    typeS = data["type"]
    what = data["request"]
    back = {"sucess":True, "userlist":[]}
    res=usersdb.search_users_by(what,typeS)
    back["sucess"]=len(res)>0
    back["userlist"]=[{"id":i['userid'],"name":i['name'],"photo":i["photo"]} for i in res]
    #back["userlist"]=[{"id":i['userid'],"email":i['email'],"name":i['name'],"photo":i["photo"],"phone":i['phone'],"about":i['about']} for i in res]
    return jsonify(back)

@app.route("/GetUserInfo",methods=["POST"])
def GetUserInfo():
    id = request.get_json()["id"]
    user=usersdb.get_user_by_id(id)
    if user["photo"]==None:
        user["photo"]="static/images/Uniknown.png"
    return jsonify({"id":user['userid'],
                    "email":user['email'],
                    "name":user['name'],
                    "photo":user["photo"],
                    "phone":user['phone'],
                    "about":user['about']})

if __name__ == '__main__':    
    app.run( host='0.0.0.0',  port=5000, debug=True, 
            ssl_context=('cert.pem',"key.pem"),
            use_reloader=False)