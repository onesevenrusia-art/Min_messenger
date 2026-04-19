import redis

class DataBase:
    def __init__(self):
        self.r=r = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True  # чтобы строки, а не bytes
    )
        
    def put(self):
        pass

    def get(self):
        pass

    def remove(self):
        pass