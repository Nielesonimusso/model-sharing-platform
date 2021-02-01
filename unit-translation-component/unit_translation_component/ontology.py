from rdflib import Graph
import os

# Declare path to module
path = os.path.abspath(__file__)
path = path[:-11]
path = path + 'om-2.ttl'

# Load module from path
OMGraph = Graph()
OMGraph.parse(location=path, format="turtle")
