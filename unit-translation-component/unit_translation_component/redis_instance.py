import redis


class RedisObject:
    # Class to interface with Redis

    # Redis instance
    __instance = None

    # Flag to indicate the redis instance is available
    __flag = None

    @staticmethod
    def get_instance():
        # Get the instance (singleton) of this class
        if RedisObject.__instance is None:
            RedisObject()
        return RedisObject.__instance

    @staticmethod
    def available():
        # Check if Redis is available and can be used
        if RedisObject.__flag is None:
            if RedisObject.__instance is None:
                RedisObject()
            RedisObject.__flag = True
            try:
                RedisObject.__instance.set("TEST", 1)
                RedisObject.__instance.delete("TEST")
            except redis.exceptions.ConnectionError:
                RedisObject.__flag = False
            return RedisObject.__flag
        else:
            return RedisObject.__flag

    def __init__(self):
        if RedisObject.__instance is not None:
            raise Exception("This is a singleton class.")
        else:
            # Initialize the Redis instance
            RedisObject.__instance = redis.StrictRedis(host="localhost", port="6379", decode_responses=True)
