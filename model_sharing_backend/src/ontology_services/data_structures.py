from dataclasses import dataclass
import dataclasses
from enum import Enum
from typing import List, Optional, Union
from marshmallow import fields, validate
from marshmallow.decorators import post_load, pre_dump

from marshmallow.schema import Schema
import rdflib

class ColumnReferenceType(str, Enum):
    NONE = 'none'
    FIXED = 'fixed'
    COLUMN = 'column'
    CONCEPT = 'concept'

    def __str__(self) -> str:
        return self.value


@dataclass
class ColumnDefinition:
    uri: str
    name: str
    datatype: str
    unit_type: ColumnReferenceType = ColumnReferenceType.NONE
    unit_uri: str = ""
    unit_source_uri: str = ""
    reference_type: ColumnReferenceType = ColumnReferenceType.NONE
    referenced_property_uri: str = ""
    referenced_object_uri: str = ""
    referenced_schema: Union['TableDefinition', List[str]] = None
    referenced_objects: List[dict] = dataclasses.field(default_factory=list)

@dataclass
class TableDefinition:
    uri: str
    columns: List[ColumnDefinition]

    #region query_methods
    @staticmethod
    def _is_unit_query(graph, column_node):
        query = f"""ASK {{ 
    ?amount a table:InterfaceObjectProperty ; 
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ] . 
}}"""
        return bool(graph.query(query))

    @staticmethod
    def _is_fixed_unit_query(graph, column_node):
        return bool(graph.query(f"""ASK {{ 
    ?amount a table:InterfaceObjectProperty ;
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ;
            omx:hasFixedUnit ?unit ] .
}}"""))

    @staticmethod
    def _is_same_table_unit_query(graph, column_node, table_node):
        return bool(graph.query(f"""ASK {{ 
    ?amount a table:InterfaceObjectProperty ;
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ;
            omx:hasUnitProperty ?unitprop ] .
    {table_node.n3()} table:hasColumnProperty ?unitprop . 
}}"""))

    @staticmethod
    def _get_unit(graph, column_node, table_node, type: ColumnReferenceType):
        if type is ColumnReferenceType.FIXED:
            return next(str(u[0]) for u in graph.query(f""" SELECT ?unit WHERE {{
    ?amount a table:InterfaceObjectProperty ;
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ;
            omx:hasFixedUnit ?unit ] . }}""")), ""
        elif type is ColumnReferenceType.COLUMN:
            return next(str(u[0]) for u in graph.query(f""" SELECT ?unit WHERE {{
    ?amount a table:InterfaceObjectProperty ;
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ;
            omx:hasUnitProperty ?unit ] . }}""")), str(table_node)
        else:
            return next(list(map(str, us)) for us in graph.query(f""" SELECT ?unit ?source WHERE {{
    ?amount a table:InterfaceObjectProperty ;
        omx:isQuantityPropertyOf [ omx:hasNumericalValueProperty {column_node.n3()} ;
            omx:hasUnitProperty ?unit ] . 
    ?unit rdfs:domain ?source . }}"""))

    @staticmethod
    def _is_reference(graph, column_node):
        return bool(graph.query(f"""ASK {{ 
    {column_node.n3()} owl3:dataTypePropertyChain ?x . 
    ?x rdf:first ?not_quantity . 
    FILTER NOT EXISTS {{ 
        ?not_quantity a table:InterfaceObjectProperty ; 
            rdfs:range om:Quantity . 
    }}
}}"""))

    @staticmethod
    def _is_table_reference(graph, column_node):
        return bool(graph.query(f"""ASK {{ 
    {column_node.n3()} owl3:dataTypePropertyChain ?x . 
    ?x rdf:first ?refobject .
    ?refobject rdfs:range ?schema .
    ?schema a table:DataSchemaClass .
}}"""))

    @staticmethod
    def _get_reference_uris(graph, column_node):
        return next(list(map(str, r)) for r in graph.query(f"""SELECT ?object ?property WHERE {{
    {column_node.n3()} owl3:dataTypePropertyChain ?x . 
    ?x rdf:first ?objref ;
        rdf:rest ?y .
    ?y rdf:first ?property .
    ?objref rdfs:range ?object .

}}"""))

    @staticmethod
    def _get_reference_properties(graph, column_node):
        return list(str(p[0]) for p in graph.query(f"""SELECT ?property WHERE {{
    {column_node.n3()} owl3:dataTypePropertyChain ?x . 
    ?x rdf:first ?objref .
    ?objref rdfs:range ?object .
    ?property rdfs:domain ?object .
}}"""))

    #endregion query_methods

    @staticmethod
    def from_graph(graph: rdflib.Graph, table_node: rdflib.URIRef) -> 'TableDefinition':
        TABLE = rdflib.Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')

        tableUri = str(table_node)

        tableColumns = []
        for column_node in graph.objects(table_node, TABLE.hasColumnProperty):
            columnUri = str(column_node)
            columnName = graph.value(subject=column_node, predicate=TABLE.hasColumnName)
            columnDatatype = next(graph.objects(column_node, rdflib.RDFS.range))

            ## units ##
            columnUnitType = ColumnReferenceType.NONE
            columnUnitUri = ""
            columnUnitSourceUri = ""
            # if there is a quantity that has this column as its numerical value
            if TableDefinition._is_unit_query(graph, column_node):
                if TableDefinition._is_fixed_unit_query(graph, column_node):
                    columnUnitType = ColumnReferenceType.FIXED
                elif TableDefinition._is_same_table_unit_query(graph, column_node, table_node): 
                    columnUnitType = ColumnReferenceType.COLUMN
                else:
                    columnUnitType = ColumnReferenceType.CONCEPT

                columnUnitUri, columnUnitSourceUri = TableDefinition._get_unit(
                    graph, column_node, table_node, columnUnitType)

            ## references ##
            referenceType = ColumnReferenceType.NONE
            referencedPropertyUri: str = ""
            referencedObjectUri: str = ""
            referencedSchema: Union['TableDefinition', List[str]] = None
            referencedObjects: List[dict] = [] # TODO fill this when location definition is available
            # if there is a chain that doesnt start with a om:Quantity property (a reference)
            if TableDefinition._is_reference(graph, column_node):
                referencedObjectUri, referencedPropertyUri = TableDefinition._get_reference_uris(graph, column_node)
                if TableDefinition._is_table_reference(graph, column_node):
                    referenceType = ColumnReferenceType.COLUMN
                    referencedSchema = TableDefinition.from_graph(graph, rdflib.URIRef(referencedObjectUri))
                else: # treat reference as concept
                    referenceType = ColumnReferenceType.CONCEPT
                    referencedSchema = TableDefinition._get_reference_properties(graph, column_node)

                # TODO change the way reference is saved? NO because extra information is necessary?
                # ...but filling in the data would require ontology to reference data source (mail!)


            tableColumns.append(ColumnDefinition(
                columnUri, columnName, columnDatatype,
                columnUnitType, columnUnitUri, columnUnitSourceUri,
                referenceType, referencedPropertyUri, referencedObjectUri, 
                    referencedSchema, referencedObjects))
        
        return TableDefinition(tableUri, tableColumns)

@dataclass
class ArgumentDefinition:
    uri: str
    name: str
    # direct from TableDefinition
    type_uri: str
    columns: List[ColumnDefinition]

    @staticmethod
    def from_graph(graph: rdflib.Graph, argument_node: rdflib.URIRef) -> 'ArgumentDefinition':
        SERVICE = rdflib.Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')

        argumentUri = str(argument_node)
        argumentName = graph.value(subject=argument_node, predicate=SERVICE.hasArgumentName)

        table_node = graph.value(subject=argument_node, predicate=SERVICE.hasArgumentType)
        tableDefinition = TableDefinition.from_graph(graph, table_node)

        return ArgumentDefinition(argumentUri, argumentName, tableDefinition.uri, tableDefinition.columns)

    
@dataclass
class ModelInterfaceDefinition:
    uri: str
    inputs: List[ArgumentDefinition]
    outputs: List[ArgumentDefinition]

    @staticmethod
    def from_graph(graph: rdflib.Graph, model_node: rdflib.URIRef = None) -> 'ModelInterfaceDefinition':
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

        return ModelInterfaceDefinition(interfaceUri, interfaceInputs, interfaceOutputs)


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
    name = fields.String(required=True)
    datatype = fields.String(required=True)
    unit_type = fields.String(default=ColumnReferenceType.NONE.value, 
        validate=validate.OneOf([a.value for a in ColumnReferenceType]))
    unit_uri = fields.String(default="")
    unit_source_uri = fields.String(default="")
    reference_type = fields.String(default=ColumnReferenceType.NONE.value, 
        validate=validate.OneOf([a.value for a in ColumnReferenceType]))
    referenced_property_uri = fields.String(default="")
    referenced_object_uri = fields.String(default="")
    referenced_schema = fields.Raw(allow_none=True) # optional Nested(TableDefinitionSchema)
    referenced_objects = fields.List(fields.Raw())

    def __init__(self, *args, **kwargs):
        super().__init__(ColumnDefinition, *args, **kwargs)


class TableDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    columns = fields.Nested(ColumnDefinitionSchema, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(TableDefinition, *args, **kwargs)


class ArgumentDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    name = fields.String(required=True)
    type_uri = fields.String(required=True)
    columns = fields.Nested(ColumnDefinitionSchema, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(ArgumentDefinition, *args, **kwargs)


class ModelInterfaceDefinitionSchema(DataclassSchema):
    uri = fields.String(required=True)
    inputs = fields.Nested(ArgumentDefinitionSchema, many=True)
    outputs = fields.Nested(ArgumentDefinitionSchema, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(ModelInterfaceDefinition, *args, **kwargs)