from unit_translation_component.redis_instance import RedisObject
import unit_translation_component.constant as ct


class TemperatureScale:
    """ This helper class is for finding the offsets of temperature units to convert between temperatures

    The offset is the offset necessary to make the unit match the kelvin scale.
    """

    def __init__(self, unit_uri):
        # First find the scale the unit belongs to (Celcius, Farenheit, Kelvin, etc)
        q_find_scale = '''
                    select ?s where {
                        ?s rdf:type ?o .FILTER regex(str(?o), "Ratio|Interval")
                        ?s <''' + ct.HAS_UNIT + '''> <''' + str(unit_uri) + '''>
                    }'''

        r_find_scale = ct.OMGraph.query(q_find_scale)
        for row in r_find_scale:
            self.label, self.URIRef = ct.trim_uri(row)

        # Get all predicates of the scale
        q_get_attr = '''
                    select ?p ?o where {
                        <''' + self.URIRef + '''> ?p ?o
                    }'''

        # Use redis cache if possible
        # Find the offset predicate and set the class's offset.
        if RedisObject.available():
            redis_instance = RedisObject.get_instance()
            if not redis_instance.exists(self.URIRef):
                r_get_attr = ct.OMGraph.query(q_get_attr)
                for pred, out in r_get_attr:
                    if str(pred) == ct.HAS_OFFSET_TEMP:
                        redis_instance.hmset(str(self.URIRef), {str(pred): str(out)})
            self.has_offset = float(redis_instance.hget(self.URIRef, ct.HAS_OFFSET_TEMP))
        else:
            r_get_attr = ct.OMGraph.query(q_get_attr)
            for pred, out in r_get_attr:
                if str(pred) == ct.HAS_OFFSET_TEMP:
                    self.has_offset = out

    def get_offset(self):
        """Get the offset attribute, this is the unit offset in kelvin"""
        if hasattr(self, 'has_offset'):
            return float(self.has_offset)
        return "undefined"
