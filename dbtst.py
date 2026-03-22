from pywebpush import webpush
from py_vapid import Vapid
import MessengerDataBase
from datetime import datetime
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