from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from email_validator import validate_email, EmailNotValidError
import Users_db
import json
simv="qwertyuioplkjhgfdsazxcvbnm@#_1234567890"

DoctypeKeys={}
usersdb = Users_db.usersDataBase()


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
        usersdb.adduser(email=data["email"], name=data["name"], phone=data["phone"], token=token)
        return jsonify({"success":True,
                        "token":token})
    else:
        return jsonify({"success":False})

@app.route("/input", methods=["POST"])
def input():
    data=request.get_json()
    token=usersdb.getUser(data["email"], ["token"])
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
    try:
        if email not in usersdb.allUsers()[0]:
            print(email,usersdb.allUsers())
            return jsonify({"state":"notreg"})
    except:jsonify({"state":"errorfind"})
    correct = IsEmailCorrect(email)
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

@app.route("/interkey2", methods=["POST"])
def dostype_2():
    data = request.get_json()
    print(DoctypeKeys)
    print(data, "z")
    if data["key"]==DoctypeKeys[data["email"]]:
        print(usersdb.getUser(data["email"],["token"]))
        return jsonify({"success":True,
                        "token":usersdb.getUser(data["email"],["token"])[0]})
    else:
        return jsonify({"success":False})      

#################################################
#################################################
#################################################

@app.route("/userchatlist",methods=["POST"])
def returnUserChatList():
    email = request.get_json()["email"]
    chats=list(usersdb.getUser(email,["chats"])[0])
    print(chats)
    if len(chats)==0:
        print("yes")
        return jsonify({"chats":json.loads(chats[0])})
    else:
        return jsonify({"chats":[{"avatar":0b0,"name":'123abcname'}]})



if __name__ == '__main__':    
    app.run( host='0.0.0.0',  port=5000, debug=True, 
            ssl_context=('cert.pem',"key.pem"),
            use_reloader=False)