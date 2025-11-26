import threading
import subprocess

def run_flask_server():
    subprocess.run(["python", "NewServerMin.py"])

def run_ws_server():
    subprocess.run(["python", "Ws_server.py"])
proc1 = threading.Thread(target=run_flask_server)
proc2 = threading.Thread(target=run_ws_server)

proc1.start()
proc2.start()
proc1.join()
proc2.join()