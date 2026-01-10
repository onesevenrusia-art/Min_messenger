a={'id': 1,
'email': 'onesevenrusia@gmail.com',
 'challenge': '48ba9342bcbeee9d32e2e5a20fed51fb42674c2c29adb4a9b8e1166ec5507aec',
   'signature': 'gA6tkWrurRJj8sCXiFmcfvofDGfrvvE5eSF7/xf/vX834Qab+K+/kWVy6q4LsFRG5t2JQH2gUhZmuGJ128L/WXkVsEnGHAgwtKl1tcRgpOSKmJkxQ0K94NaQrkRUIGeav8XpQNr+/T80wVBY0NmrYQzT4cbOlXGUaUELjrvoT+l92+dYZiV9hHVBrm6el0QMlishpFxuqIqXUlUewYsCFNpb3/8ajyjj39vFb2tuOKbX28SrwAEbhuUtod28BvuwKobJO+v7Iz5TYuTdWru/hrz2mdNBq5wdJBcEe+I+Va4Bi6jYSYqhGszWfu/ou9VEFT7m79+xR3rRNCuaYf0ppA==',
     'device': 'chrome-a_LF0Nv6Jce_6vXLsvCXZOFc1ZD', 
     'what': {'x': 'auth'}}

b={'id': 1,
'email': 'onesevenrusia@gmail.com',
 'name': 'Alex',
   'phone': '72845639801',
     'about': None,
       'photo': None,
         'blocked': None, 
         'devices': [{'id': 1, 'name': 'chrome-a_LF0Nv6Jce_6vXLsvCXZOFc1ZD', 'platform': 'Windows', 'last_seen': 'datetime.datetime(2025, 12, 26, 20, 28, 32, 454302)', 
                      'publickey': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4F23X++IMDX0XmL9Np63+CyvwVvcFu9qCs3+H78Q4d8MHHZpHF8peesLIVu+sL6Epdcdbzsy3GOH7VFievvco4SGfTOUqRp7YDoNaGDrVUi5JAg10IPC/R7FfEMLaISSAupt519SxUwWUt9IU6aI+2uHUi8SgHlFNhXhrk11z24zAGKLFmUHRBAUqJYI/UgdgUrOWDkfMErlPoobeVpwTA4jLJ7sQ4l5z9gbCRluBtcBVhcMFuL0GLH4VkGbqg5dVfvwSC6ivoo7Xz+NEIQAarsn/NfpOVGewVlbzUeEmkKrp3G2RZj+LQQfBWP3KFiRhTNMYZ59tZ9FBjlzd58+ZQIDAQAB', 'publickeycrypt': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzMWpi7gEj6APRBFKwhTcMvK9uQzWxIfZflkYV5JEzam7cSydg2NsNHryBagRMJgyKBjiR0wpvFkJ9Ym/97ikciuJoH/qgYowz3eSYst7TfokNDR7wk7xcSr3RptxYG5pn8c/nEfs1UtVifhBoYnvz5TRUPzAI12sr+bMCHHa/Xd7gyabHIOjcfkpkxF0NwYXg8/qsJ4CEl5WYa+t10EcmwfXKPNOvxAEPPhVC+gXO2kdzJscmT5HunAQKez0uVRVTOeCGaUKUMC3/eq14aFFmBMkY7wf/42zhFUw7mg4knQGZhTftjA271K2T+U4YNu7RllpDial6+tRYtrBg1JOowIDAQAB'}]}
print(list(filter(lambda x: x["name"]==2 , [{"name":2},{"name":1}])))
print( list(filter(lambda x: x["publickey"]  is not None, b["devices"])))
print(a['device'] in b['devices'])
import MessengerDataBase
db = MessengerDataBase.DataBaseManager()
#db.add_Inventive("arcsaeaga@gmail.com","onesevenrusia@gmail.com","new_chat")
#for inventive in db.get_user_Inventives("arcsaraga@gmail.com"):
#    db.delete_Inventive(inventive["id"])
db.delete_Chat(3)
