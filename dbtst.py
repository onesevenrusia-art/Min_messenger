from pywebpush import webpush
from py_vapid import Vapid
import MessengerDataBase
from datetime import datetime
#v = Vapid()
#v.generate_keys()
#print("PRIVATE:", v.private_key)
#print("PUBLIC:", v.public_key)

Database = MessengerDataBase.DataBaseManager()
s = Database.get_Events_before(1,datetime.now())
print(s)
for i in {1:"a",2:"b"}:
    print(i)