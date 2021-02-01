import unit_translation_component.constant as ct
from unit_translation_component.redis_instance import RedisObject


class Prefix:
    def __init__(self, URI: str):
        self.URIref = URI
        q_get_attr = '''
                    select ?p ?o where {
                        <''' + str(self.URIref) + '''> ?p ?o
                    }'''

        # In redis_instance.py is a flag that is set to true if
        # the connection to the redis server is succesfull. If
        # it's not, then proceed with normal querying.
        if RedisObject.available():
            # If the prefix is not cached, cache and load it.
            redis_instance = RedisObject.get_instance()
            if not redis_instance.exists(URI):
                r_get_attr = ct.OMGraph.query(q_get_attr)
                for pred, out in r_get_attr:
                    if str(pred) == ct.HAS_FACTOR:
                        redis_instance.hmset(str(URI), {str(pred): str(out)})
            # If there is a key present in redis, there is no need
            # for additional caching. Load it directly from redis.
            self.has_factor = float(redis_instance.hget(str(URI), ct.HAS_FACTOR))
        else:
            r_get_attr = ct.OMGraph.query(q_get_attr)
            for pred, out in r_get_attr:
                if str(pred) == ct.HAS_FACTOR:
                    self.has_factor = out

    def get_factor(self):
        if hasattr(self, 'has_factor'):
            return self.has_factor
        return 1.0
