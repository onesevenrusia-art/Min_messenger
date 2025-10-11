import socket

ip = "91.121.209.114"
port = 1080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)

try:
    sock.connect((ip, port))
    print("Порт открыт, соединение установлено")
except socket.timeout:
    print("Таймаут: сервер не отвечает")
except socket.error as e:
    print("Ошибка:", e)
finally:
    sock.close()