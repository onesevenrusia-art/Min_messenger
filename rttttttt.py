import vrotayadb
userdb=vrotayadb.UserManager()
user=userdb.get_user_by_id(7)
print(user["devices"][next(iter(user["devices"].keys()))] )
