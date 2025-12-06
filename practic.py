from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("test.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
{'email': 'ded@gmail.com', 
 'device': {'platform': 'Linux aarch64',
             'userAgent': 'Mozilla/5.0 (Linux; arm_64; Android 14;'
             ' CLK-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.952 YaSearchBrowser/25.106.1 BroPP/1.0 YaSearchApp/25.106.1 webOmni SA/3 Mobile Safari/537.36',
               'language': 'ru-RU',
                 'languages': ['ru-RU', 'ru', 'en-US', 'en'], 
                 'hardwareConcurrency': 8,
                   'deviceMemory': 8,
                     'screen': {'width': 360, 'height': 804, 'colorDepth': 24, 'pixelDepth': 24},
                       'timezone': 'Europe/Moscow', 'timezoneOffset': -180},
   'publickey': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx6lmEVY2T1U3+QrF7m78xGhzo2aZ6gaH7HbcucjgZP+Bu3C7wn150/KPZ51v19XRa5IXiyNzutlPfykYq2xzbUvG72WcHeZiAt4xvHMxtRQGgTMa0THNgctq8fvu2KBQAy03esDnGGiHEtKO9JoBLHlOIvn+Iz3i0fWzGyYleva9qCasKcM/8P1pwGoYKMXSnkj2uHX+vXAXBpKAWxV99F5NBHwqmXlY53EdD8yx9n1pxzv9UII6X75B8KwREPLvzLKdkfBo6CMOAX/fH0weBsYcW/qwdiEehQKAUb+JSMXbyAzEHqZ7u4OhOdPXFRgmK1O3nLhQxxp9GL2Zt9ivCQIDAQAB',
     'fingerprint': {}, 
     'type': 'newdevice'}
{'ded@gmail.com': {'fingerprint': {}, 'ip': '192.168.1.71'}}

if __name__ == '__main__':    
    app.run( host='0.0.0.0',  port=5000, debug=True, 
            ssl_context=('cert.pem',"key.pem"),
            use_reloader=False) 
