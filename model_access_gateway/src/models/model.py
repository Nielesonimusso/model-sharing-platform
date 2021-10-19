from abc import ABCMeta, abstractmethod
from functools import reduce
import json, os
from typing import Dict, List, Tuple
from flask import current_app

from logging import getLogger
from json import dumps
from rdflib import Namespace, RDF, RDFS, XSD, OWL

from marshmallow import fields
import rdflib
from rdflib.graph import Graph
from rdflib.term import BNode, Literal, URIRef
from rdflib.collection import Collection

class Model(metaclass=ABCMeta):

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @abstractmethod
    def run_model(self, input) -> Dict[str, List[dict]]:
        pass

    @property
    @abstractmethod
    def input_dto(self) -> type:
        pass

    @property
    @abstractmethod
    def output_dto(self) -> type:
        pass

    @property
    @abstractmethod
    def ontology_imports(self) -> List[Tuple[rdflib.URIRef, str]]:
        pass

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def price(self) -> float:
        pass

    def get_ontology(self) -> str:
        ROOT = Namespace('#')
        OM = Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
        OMX = Namespace('http://www.foodvoc.org/resource/InternetOfFood/omx/')
        TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')
        SERVICE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Service/')
        OWL3 = Namespace('http://www.foodvoc.org/resource/InternetOfFood/OntologyWebLanguage/') # BUG IMAGINARY OWL

        og = Graph()
        og.namespace_manager.bind('', ROOT)
        og.namespace_manager.bind('om', OM)
        og.namespace_manager.bind('omx', OMX)
        og.namespace_manager.bind('table', TABLE)
        og.namespace_manager.bind('service', SERVICE)
        og.namespace_manager.bind('owl3', OWL3)
        og.namespace_manager.bind('owl', OWL) # BUG should be included by default, but isnt?

        ### base definitions ###
        ## ontology definition ##
        og.add((ROOT[''], RDF.type, OWL.Ontology))

        ## ontology imports ##
        for imported, imported_prefix in self.ontology_imports:
            # also add namespace
            og.namespace_manager.bind(imported_prefix, Namespace(imported))
            og.add((ROOT[''], OWL.imports, URIRef(imported[:-1])))

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
            graph.add((ROOT[table_name], RDF.type, TABLE.DataSchemaClass))

            for column_name, column_type in column_list:
                column_uri = ROOT[table_name + "_" + column_name]
                graph.add((ROOT[table_name], TABLE.hasColumnProperty, column_uri))

                graph.add((column_uri, RDF.type, TABLE.ColumnProperty))
                graph.add((column_uri, RDFS.domain, ROOT[table_name]))
                graph.add((column_uri, RDFS.range, column_type))
                graph.add((column_uri, TABLE.hasColumnName, Literal(column_name)))

        def handle_unit_defs(table_name, table_object, graph) -> None:
            unit_defs = table_object.units
            table_columns = table_columns_from_table_object(table_object)
            for column_name, column_type in table_columns:
                if unit_defs[column_name] is not None: # there is a unit definition
                    column_uri = ROOT[table_name + "_" + column_name]
                    is_fixed = isinstance(unit_defs[column_name], rdflib.URIRef)
                    from_ontology = isinstance(unit_defs[column_name], dict)

                    # quantity object-property (column_nameQuantity)
                    graph.add((ROOT[column_name + "Quantity"], RDF.type, TABLE.InterfaceObjectProperty))
                    graph.add((ROOT[column_name + "Quantity"], RDFS.domain, ROOT[table_name]))
                    graph.add((ROOT[column_name + "Quantity"], RDFS.range, OM.Quantity))

                    # unit object-property (with fixed domain)
                    if is_fixed:
                        graph.add((ROOT[column_name + "Unit"], RDF.type, TABLE.InterfaceObjectProperty))
                        graph.add((ROOT[column_name + "Unit"], RDFS.domain, ROOT[table_name]))
                        graph.add((ROOT[column_name + "Unit"], RDFS.range, OM.Unit))
                        # restriction on unit InterfaceObjectProperty to only be the fixed unit
                        objectRestriction = BNode()
                        graph.add((objectRestriction, RDF.type, OWL.restriction))
                        graph.add((objectRestriction, OWL.onProperty, ROOT[column_name + "Unit"]))
                        graph.add((objectRestriction, OWL.toValue, unit_defs[column_name]))
                        graph.add((ROOT[table_name], RDFS.subClassOf, objectRestriction))

                    # quantity isQuantityPropertyOf [value=column_nameValue, unit=unit_defs[column_name]]
                    quantity_node = BNode()
                    graph.add((quantity_node, OMX.hasNumericalValueProperty, column_uri))
                    if is_fixed:
                        graph.add((quantity_node, OMX.hasFixedUnit, unit_defs[column_name]))
                    else:
                        graph.add((quantity_node, 
                            OMX.hasUnitProperty, 
                            ROOT[table_name + "_" + unit_defs[column_name]]))
                    graph.add((ROOT[column_name + "Quantity"], OMX.isQuantityPropertyOf, quantity_node))

                    # value dataTypePropertyChain 
                    valuePropertyChain = BNode()
                    Collection(graph, valuePropertyChain, [
                        ROOT[column_name + "Quantity"],
                        OM.hasValue, 
                        OM.hasNumericalValue
                    ])
                    graph.add((column_uri, OWL3.dataTypePropertyChain, valuePropertyChain))

                    # unit dataTypePropertyChain
                    unitPropertyChain = BNode()
                    if is_fixed:
                        Collection(graph, unitPropertyChain, [
                            ROOT[column_name + "Quantity"],
                            OM.hasValue, 
                            OM.hasUnit
                        ])
                        # unit objectproperty as chain
                        graph.add((ROOT[column_name + "Unit"], 
                            OWL3.dataTypePropertyChain, unitPropertyChain))
                    else:
                        Collection(graph, unitPropertyChain, [
                            ROOT[column_name + "Quantity"],
                            OM.hasValue, 
                            OM.hasUnit,
                            OM.symbol
                        ])
                        # unit source columnproperty as chain
                        graph.add((ROOT[table_name + "_" + unit_defs[column_name]], 
                            OWL3.dataTypePropertyChain, 
                            unitPropertyChain))

                    

        def handle_reference_defs(table_name, table_object, graph) -> None:
            reference_defs = table_object.references
            table_columns = table_columns_from_table_object(table_object)
            for column_name, column_type in table_columns:
                if reference_defs[column_name] is not None: # there is a reference definition
                    column_uri = ROOT[table_name + "_" + column_name]
                    # to create:
                        # InterfaceObjectProperty
                    graph.add((ROOT[column_name + "Object"], RDF.type, TABLE.InterfaceObjectProperty))
                    graph.add((ROOT[column_name + "Object"], RDFS.domain, ROOT[table_name]))
                    graph.add((ROOT[column_name + "Object"], RDFS.range, reference_defs[column_name]["source"]))
                        # dataTypePropertyChain
                    referencePropertyChain = BNode()
                    Collection(graph, referencePropertyChain, [
                        ROOT[column_name + "Object"],
                        reference_defs[column_name]["property"]
                    ])

                    graph.add((column_uri, OWL3.dataTypePropertyChain, referencePropertyChain))

        def handle_interface_dto(dto, graph, is_input):
            # gather tables from dto
            tables = {name: field.schema
                for name, field
                in dto._declared_fields.items()
                if issubclass(type(field), fields.Nested)}

            # handle each table
            for table_name, table_object in tables.items():
                ## table definitions ##
                table_columns = table_columns_from_table_object(table_object)
                table_def_from_name_and_column_list(table_name, table_columns, graph)

                ## argument definitions ##
                graph.add((ROOT[("input__" if is_input else "output__")+table_name], RDF.type, SERVICE.InputArgument if is_input else SERVICE.OutputArgument))
                graph.add((ROOT[("input__" if is_input else "output__")+table_name], SERVICE.hasArgumentName, Literal(table_name)))
                graph.add((ROOT[("input__" if is_input else "output__")+table_name], SERVICE.hasArgumentType, ROOT[table_name]))
                ## relation between argument and model ##
                graph.add((ROOT[type(self).__name__], 
                    SERVICE.hasInputArgument if is_input else SERVICE.hasOutputArgument, 
                    ROOT[("input__" if is_input else "output__")+table_name]))

                handle_unit_defs(table_name, table_object, graph)
                handle_reference_defs(table_name, table_object, graph)

        ### model definition ###
        og.add((ROOT[type(self).__name__], RDF.type, SERVICE.Model))

        ## table and argument definitions for inputs ##
        handle_interface_dto(self.input_dto, og, True)

        ## table and argument definitions for outputs ##
        handle_interface_dto(self.output_dto, og, False)

        return og.serialize(format='turtle')

def get_model_ontology_dependency(name: str) -> str:
    return json.loads(os.getenv('MODEL_DEPENDENCY_GATEWAY_URLS', '{}')).get(name)