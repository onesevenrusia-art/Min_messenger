from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("testimage.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

#MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVgJ8pMSAQdaEn8B+o4smM8/c1f9Vy9KEr19H8wp3k3euRZjs+A6c6Or9KiHdOeMZgRkvq/x2RMdg3fpV7pU2Dv1xWIblm0PaSFynURvnPCJVf+xIvHGrNeQMugY4KI58GoNMGeB/ckFH0Gtq2b4Ry5FPSxbLlRFIXoMNZBxnkrRgkIpGkBi7Si3pOF2tBwSfAbIHU/Du94tIAda1+o2LHGevKAZYjTfT5xMcvHDT1HJu9mEy1QPcyt+59cgc0gmAq61NjnNEmj3ay0sgcPK+Cz0yBxkeZy71Z9aIE3KC6P6OjEzHjsIbyjGijAZrbWOY+GJ6ZBKzHsvq4S0AhmNwQIDAQAB
#MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVgJ8pMSAQdaEn8B+o4smM8/c1f9Vy9KEr19H8wp3k3euRZjs+A6c6Or9KiHdOeMZgRkvq/x2RMdg3fpV7pU2Dv1xWIblm0PaSFynURvnPCJVf+xIvHGrNeQMugY4KI58GoNMGeB/ckFH0Gtq2b4Ry5FPSxbLlRFIXoMNZBxnkrRgkIpGkBi7Si3pOF2tBwSfAbIHU/Du94tIAda1+o2LHGevKAZYjTfT5xMcvHDT1HJu9mEy1QPcyt+59cgc0gmAq61NjnNEmj3ay0sgcPK+Cz0yBxkeZy71Z9aIE3KC6P6OjEzHjsIbyjGijAZrbWOY+GJ6ZBKzHsvq4S0AhmNwQIDAQAB
#MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAk79HpfLZjkJCVSffJxZsWJ77Z5TTMd0UYf9d8mnDGtegg29iRK/P1r7ldHzbjLWQUQGagZshQ6qV94HKRZeJN7lcaHoRFog7aYbdZv42XDkfcjNlcSwR8I6BEREfds0bHCcK8NJQB9G7djj+fcSPVUCPJA2Xb/XtqD5833wkcR1TWH331xNnEP6f6AbdyemEiqVC9hUfOX37GUrNQkfcZqIUArEva87Y463xerOERkwXVBUTPzLC13KvB0Tqx78yKdzLo8UivZI1CuHLIjikBWXu++XJEOVQwKUR95hk+XZrnbfBd2ljY4Tr9YzRQDxOD8rQzjhMvWtNKV/YoXyEFwIDAQAB
if __name__ == '__main__':    
    app.run( host='0.0.0.0',  port=5000, debug=True, 
            ssl_context=('cert.pem',"key.pem"),
            use_reloader=False) 
    

  
