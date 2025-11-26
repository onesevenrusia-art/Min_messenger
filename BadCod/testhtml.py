from flask import Flask, request, jsonify, render_template, send_from_directory
import BadCod.Users_db as Users_db
import json

usersdb = Users_db.usersDataBase()

app = Flask(__name__)

@app.route("/r")
def index():
    return render_template("reciver.html")

@app.route("/t")
def inde2x():
    return render_template("sender.html")

@app.route("/")
def index3():
    return render_template("messenger.html")

@app.route("/userchatlist",methods=["POST"])
def returnUserChatList():
    email = request.get_json()["email"]
    chats=json.loads( usersdb.getUser(email,["chats"]))
    print(chats)
    print(chats)
    return jsonify({"chats":chats})

if __name__ == '__main__':    
    app.run(ssl_context=("cert.pem", "key.pem"), host='0.0.0.0',  port=5000, debug=True,  use_reloader=False)