import redis
import json

class DataBase:
    def __init__(self):
        try:
            self.r = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=True
            )
            self.r.ping()
            self.r_flaf = True
        except:
            self.r = {}
            self.r_flaf = False

    def put(self, key, data, ttl=None):
        """
        Сохраняет данные.
        data может быть str / dict / list
        ttl — время жизни в секундах
        """
        if not self.r_flaf:
            self.r[str(key)]=data
            return
        if not isinstance(data, str):
            data = json.dumps(data)
        if ttl:
            self.r.setex(key, ttl, data)
        else:
            self.r.set(key, data)


    def get(self, key):
        """
        Возвращает данные (пытается распарсить JSON)
        """
        value = self.r.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except:
            return value

    def remove(self, key):
        """
        Удаляет ключ
        """
        self.r.delete(key)
