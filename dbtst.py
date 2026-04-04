from pywebpush import webpush
from py_vapid import Vapid
import MessengerDataBase
import datetime
#v = Vapid()
#v.generate_keys()
#print("PRIVATE:", v.private_key)
#print("PUBLIC:", v.public_key)

Database = MessengerDataBase.DataBaseManager()
#z=Database.add_device(1,"enc","z","e","macos",)
d = Database.get_messages_more_less(1,1,5,0)
print(d)
"""
s = Database.get_Events_before(1,datetime.now())
print(s)
p=[{'id': 1}, {'id': 2}]
f=[False,-1]
for k in p:
    print(k["id"])
    if k["id"]==str(2):
        f[0]=True
    else:f[1]=k["id"]
if f[0] and f[1]!= -1:
    print("ok")

print("mx",max({1:8,2:7}.keys()))

print()
"""
print(len([{'id': 1, 'name': 'chrome-8NPw7J4zSMG5FOdd01m5uNeH#Z@9J3xog', 'platform': 'Windows', 'last_seen': datetime.datetime(2026, 4, 1, 22, 22, 49, 643892), 'subscription_data': {}}, {'id': 4, 'name': 'chrome-BceVVG3wm_qLDPAHsCH5_LNZx2zaCcZ40p', 'platform': 'Linux', 'last_seen': datetime.datetime(2026, 4, 1, 22, 23, 32, 302188), 'subscription_data': {}}, {'id': 5, 'name': 'firefox-ps9S@u8oVD0@1Qaf8j#1y32HvqX3s9', 'platform': 'Windows', 'last_seen': datetime.datetime(2026, 4, 1, 22, 26, 32, 174265), 'subscription_data': {}}]  ))