from unit_translation_component.redis_instance import RedisObject
from unit_translation_component.ontology import OMGraph
import unit_translation_component.constant as ct


# Dimension class creates a dictionary for each dimension consisting of all
# properties and their values, where the dimension is given as a URIref through arg_dim
class Dimension:
    # Represents a dimension

    # Creates a dictionary for each dimension consisting of all
    # properties and their values, where the dimension is given as a URIref through arg_dim

    def __init__(self, arg_dim: str):
        self.values = {}
        self.name = arg_dim
        # For each property in SI_properties query the OM2 graph for the corresponding value
        # and save it as a new entry in the dictionary
        if RedisObject.available():
            self.__redis_init()
        else:
            self.__standard_init()

    def __redis_init(self):
        redis_instance = RedisObject.get_instance()
        if not redis_instance.exists(self.name):
            for pred in ct.SI_properties:
                value = '''
                    select ?o where {
                        <''' + str(self.name) + '''> <''' + ct.OM2 + pred + '''> ?o
                    }'''
                r = OMGraph.query(value)
                if len(r) > 0:
                    for res in r:
                        redis_instance.hmset(str(self.name), {str(pred): str(res[0])})
                else:
                    redis_instance.hmset(str(self.name), {str(pred): '0'})
        for pred in ct.SI_properties:
            self.values[pred] = int(redis_instance.hget(str(self.name), pred))

    def __standard_init(self):
        for pred in ct.SI_properties:
            value = '''
                select ?o where {
                    <''' + str(self.name) + '''> <''' + ct.OM2 + pred + '''> ?o
                }'''
            for res in OMGraph.query(value):
                self.values[pred] = int(res[0])
        for pred in ct.SI_properties:
            if pred not in self.values:
                self.values[pred] = 0

    def dim_equals(self, to_dim):
        # Checks if two dimensions are equal
        for x in self.values:
            if self.values[x] != to_dim.values[x]:
                return False
        return True

    def dim_sum(self, arg_dim):
        # Sums two dimensions SI values
        for x in self.values:
            self.values[x] = self.values[x] + arg_dim.values[x]
        return self

    def dim_sub(self, arg_dim):
        # Subtracts two dimensions SI values
        for x in self.values:
            self.values[x] = self.values[x] - arg_dim.values[x]
        return self
