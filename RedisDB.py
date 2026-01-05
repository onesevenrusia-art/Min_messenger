import redis
import json

class RedisManager:
    def __init__(self, host="localhost", port=6379):
        self.r = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )

    def _key(self, namespace: str, key: str | int) -> str:
        return f"{namespace}:{key}"

    def h_set(self, ns, key, field, value, ttl=None):
        rkey = self._key(ns, key)
        self.r.hset(rkey, field, json.dumps(value))
        if ttl:
            self.r.expire(rkey, ttl)

    def h_get(self, ns, key, field):
        rkey = self._key(ns, key)
        val = self.r.hget(rkey, field)
        return json.loads(val) if val else None

    def h_getall(self, ns, key):
        rkey = self._key(ns, key)
        return {k: json.loads(v) for k, v in self.r.hgetall(rkey).items()}

    def h_del(self, ns, key, field=None):
        rkey = self._key(ns, key)
        if field:
            self.r.hdel(rkey, field)
        else:
            self.r.delete(rkey)

db = RedisManager()
