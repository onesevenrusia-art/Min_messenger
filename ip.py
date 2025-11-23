import requests
import vrotayadb
usersdb = vrotayadb.UserManager()
ip =input() # замените на нужный IP, например, свой внешний
response = requests.get(f"https://ipinfo.io/{ip}/json")
data = response.json()
ipmy = requests.get("https://api64.ipify.org?format=json").json()["ip"]
print(ipmy)
print(f"Ваш IP: {ip}")
print(f"IP: {data.get('ip')}")
print(f"Город: {data.get('city')}")
print(f"Регион: {data.get('region')}")
print(f"Страна: {data.get('country')}")
print(f"Организация: {data.get('org')}")
print(f"Координаты: {data.get('loc')}")

usersdb.update_user(email="pokrytay@gmail.com",phone="89756483321")