import MessengerDataBase
db = MessengerDataBase.DataBaseManager()
r = db.get_Events_before(2, "2026-04-25 18:15:40.509557")
print(r)