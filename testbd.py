import MessengerDataBase
db = MessengerDataBase.DataBaseManager()
r = db.get_max_msgid(5)
print(r)