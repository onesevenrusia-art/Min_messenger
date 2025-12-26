import MessengerDataBase
Database = MessengerDataBase.DataBaseManager()
"""
res=Database.add_user(email="onesevenrusia@gmail.com",
                  name="Alex",
                  phone="7888654688",
           )
print(res)
if res["success"]:

    Database.add_device(user_id=res["user_id"],
                        name="chrome-R7FI#Mya0wjoD4Q28qC65s2OT9v1",
                        platform="windows",
                        publickey="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA00hEeIsdgPBWusBehAWkN254iyhBMBNooWcrZ3os1x2WNnGyz9d87Mqr4d5oYp4ZfAoNj8/Cn3TocJLYcUSkQR62rIInJ04okncYqfrMSLh7CywJvecFxPkkoy0F48RLTQG6EKriesp0w878nL9BERIGHQiBNYNvCfEoywu6Y7zmC+7J1eVm63h5ULtM406heL07TZ3tk89L67X0cp6V04Rm7O3pDWWFenlX9YXwEbHwQzGu2yYhusV2ZY1rgWPPT3Dw9kfc5jckHo/PQE/6C75K54akmbZChwkkwLskz2Z0RwIvh/x6ubmmB7RaBe7BP4sGVoRy8DfStLsh022+awIDAQAB",
                        publickeycrypt='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwiqX2qsDGVg6PSpfdIdfvDkgia0tptrL0BrHldyIpExj6TVR+cKMdAx1PVBChLCBt6lwAfFJJTpNaejkVuGn+Ji/QxEBQ/IsHo8dp+HnDfznG9Z0MFQSK6PzbGLZf/TAQPMFCbTlnSkH1+2qfiMR11aiYWpiala9dE2/scGz+R5NnXd6x8fGdorqBODiyDDms1CpLFbFOcYmL+XbESIONhojlutNKWTpl3y6M53zH/FQwSsHSsasqBk1lK0lvinxcUgEtb+Jdyf5ZDpE0ed4SizOkfQ+WpcieLFNoeE23FsGNKuuMvR4PLFkhrFyZUnGCv+PUEf/+iz5FUtn4l9nTwIDAQAB',
                        )
    user_id=res["user_id"]
    res=Database.add_chat(
        name="MIN поддержка",
        user_ids=[res["user_id"]],
        about="Технический чат",
        photo="static/images/logo.png"
    )
    if res["success"]:
        Database.add_message(
            chat_id=res["chat_id"],
            user_id=user_id,
            datatype="txt",
            content="успешно создан чат"
        )
    """
print(Database.get_user_by_email("onesia@gmail.com"))
print(Database.get_user_chats(1))