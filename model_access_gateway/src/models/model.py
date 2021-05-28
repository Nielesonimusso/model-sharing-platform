from abc import ABCMeta, abstractmethod
from functools import reduce
from typing import List, Tuple
from flask import current_app

from logging import getLogger
from json import dumps
from rdflib import Namespace, RDF, RDFS, XSD, OWL

from marshmallow import fields
from rdflib.graph import Graph
from rdflib.term import Literal, URIRef

class Model(metaclass=ABCMeta):

    @abstractmethod
    def run_model(self, input) -> List[dict]:
        pass

    @property
    @abstractmethod
    def input_dto(self) -> type:
        pass

    @property
    @abstractmethod
    def output_dto(self) -> type:
        pass

    def get_ontology(self) -> str:
        ROOT = Namespace('#')
        TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')
        SERVICE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')

        og = Graph()
        og.namespace_manager.bind('', ROOT)
        og.namespace_manager.bind('table', TABLE)
        og.namespace_manager.bind('service', SERVICE)

        ### table definitions ###
        ## table definition helper functions ##
        def xsd_type(field_object) -> URIRef:
            if issubclass(type(field_object), fields.Number):
                return XSD[field_object.num_type.__name__.lower()]
            else:
                return XSD[type(field_object).__name__.lower()]

        def table_columns_from_table_object(table_object) -> List[Tuple[str, URIRef]]:
            return [(column_name, xsd_type(field_object)) 
                for column_name, field_object in table_object._declared_fields.items()]

        def table_def_from_name_and_column_list(table_name, column_list, graph) -> None:
            graph.add((ROOT[table_name], RDF.type, TABLE.DataTableClass))

            for column in column_list:
                graph.add((ROOT[table_name], TABLE.hasColumnProperty, ROOT[column[0]]))

                graph.add((ROOT[column[0]], RDF.type, TABLE.ColumnProperty))
                graph.add((ROOT[column[0]], RDFS.domain, ROOT[table_name]))
                graph.add((ROOT[column[0]], RDFS.range, column[1]))
                graph.add((ROOT[column[0]], TABLE.hasColumnName, Literal(column[0])))

        ## gather input table definitions from schemas ##
        input_tables = {name: field.schema
            for name, field
            in self.input_dto._declared_fields.items()
            if issubclass(type(field), fields.Nested)}

        for table_name, table_object in input_tables.items():
            input_tables[table_name] = table_columns_from_table_object(table_object)
        
        ## input table definitions ##
        for table_name, column_list in input_tables.items():
            table_def_from_name_and_column_list(table_name, column_list, og)

        ## gather output table definition from schema ##
        output_table_object = self.output_dto()
        output_table_name = type(output_table_object).__name__.\
            replace("Dto", "").replace("Schema", "")

        output_column_list = table_columns_from_table_object(output_table_object)

        ## output table definition ##
        table_def_from_name_and_column_list(output_table_name, output_column_list, og)

        ### model definition ###
        ## argument definition ##
        # input arguments
        for table_name in input_tables.keys():
            og.add((ROOT["input__"+table_name], RDF.type, SERVICE.InputArgument))
            og.add((ROOT["input__"+table_name], SERVICE.hasArgumentName, Literal(table_name)))
            og.add((ROOT["input__"+table_name], SERVICE.hasArgumentType, ROOT[table_name]))

        # output argument
        og.add((ROOT["output__"+output_table_name], RDF.type, SERVICE.OutputArgument))
        og.add((ROOT["output__"+output_table_name], SERVICE.hasArgumentName, Literal(output_table_name)))
        og.add((ROOT["output__"+output_table_name], SERVICE.hasArgumentType, ROOT[output_table_name]))

        ## main definition ##
        og.add((ROOT[type(self).__name__], RDF.type, SERVICE.Model))
        for table_name in input_tables.keys():
            og.add((ROOT[type(self).__name__], SERVICE.hasInputArgument, ROOT["input__"+table_name]))
        og.add((ROOT[type(self).__name__], SERVICE.hasOutputArgument, ROOT["output__"+output_table_name]))
        
        # TODO load and add external ontology definition
        # ... or add external data source references + value*unit definitions to code

        return og.serialize(format='turtle')