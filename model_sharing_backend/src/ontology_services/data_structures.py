from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union
from marshmallow import fields
from marshmallow.decorators import post_load

from marshmallow.schema import Schema
import rdflib

@dataclass
class ColumnDefinition:
    uri: str
    datatype: str
    unit: str = None
    value_source: str = None

@dataclass
class ArgumentDefinition:
    uri: str
    name: str
    type_uri: str
    columns: List[ColumnDefinition]

    @staticmethod
    def from_graph(graph: rdflib.Graph, argument_node: rdflib.URIRef) -> 'ArgumentDefinition':
        SERVICE = rdflib.Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')
        TABLE = rdflib.Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')

        argumentUri = str(argument_node)
        argumentName = graph.value(subject=argument_node, predicate=SERVICE.hasArgumentName)

        table_node = graph.value(subject=argument_node, predicate=SERVICE.hasArgumentType)
        argumentTypeUri = str(table_node)

        tableColumns = []
        for column_node in graph.objects(table_node, TABLE.hasColumnProperty):
            columnUri = str(column_node)
            columnDatatype = next(graph.objects(column_node, rdflib.RDFS.range))
            #TODO columnUnit and columnValue_source
            tableColumns.append(ColumnDefinition(columnUri, columnDatatype))

        return ArgumentDefinition(argumentUri, argumentName, argumentTypeUri, tableColumns)

    
@dataclass
class InterfaceDefinition:
    uri: str
    inputs: List[ArgumentDefinition]
    outputs: List[ArgumentDefinition]

    @staticmethod
    def from_graph(graph: rdflib.Graph, model_node: rdflib.URIRef = None) -> 'InterfaceDefinition':
        SERVICE = rdflib.Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')

        # pick first model subject in graph if no model node is provided
        try:
            root_node = model_node if model_node else next(graph.subjects((rdflib.RDF.type, SERVICE.Model)))
        except StopIteration:
            raise ValueError('The provided graph does not contain a model')

        interfaceUri = str(root_node)
        interfaceInputs = [ArgumentDefinition.from_graph(graph, input_node) 
            for input_node in graph.objects(root_node, SERVICE.hasInputArgument)]
        interfaceOutputs = [ArgumentDefinition.from_graph(graph, output_node) 
            for output_node in graph.objects(root_node, SERVICE.hasOutputArgument)]

        return InterfaceDefinition(interfaceUri, interfaceInputs, interfaceOutputs)


class DataclassSchema(Schema):

    def __init__(self, data_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unknown = 'EXCLUDE'
        self._data_type = data_type

    @post_load
    def _after_load(self, data, **kwargs):
        return self._data_type(**data)

class ColumnDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    datatype = fields.String(required=True)
    unit = fields.String(missing=None)
    value_source = fields.String(missing=None)

    def __init__(self, *args, **kwargs):
        super().__init__(ColumnDefinition, *args, **kwargs)

class ArgumentDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    name = fields.String(required=True)
    type_uri = fields.String(required=True)
    columns = fields.Nested(ColumnDefinitionSchema, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(ArgumentDefinition, *args, **kwargs)

class InterfaceDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    inputs = fields.Nested(ArgumentDefinitionSchema, many=True)
    outputs = fields.Nested(ArgumentDefinitionSchema, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(InterfaceDefinition, *args, **kwargs)