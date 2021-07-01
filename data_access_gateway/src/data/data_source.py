from typing import List, Tuple, Dict
from functools import reduce
import csv
from os.path import splitext, basename

from rdflib import Namespace, RDF, RDFS, XSD
from rdflib.term import BNode, URIRef, Literal
from rdflib.graph import Graph
from rdflib.collection import Collection

class DataSource:
    def __init__(self, data_path, ontology_path, column_info, name):
        self.data_path = data_path
        self.ontology_path = ontology_path
        self.column_info = column_info

        self.name = name
        self.id = None

    def get_field_names(self) -> List[str]:
        fields = list()
        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)
            fields = reader.fieldnames
        return fields

    def _column_type_mapping(self, data_type) -> URIRef:
        return XSD[data_type]

    def _get_column_type(self, column) -> type:
        return eval(self.column_info[column]['data_type'])

    def get_rows(self, columns: Tuple[str, ...], unique: bool) -> List[dict]:

        rows = list()

        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)

            for line in reader:
                rows.append({column: self._get_column_type(column)(line[column]) for column in columns})
            
            if unique:
                rows = reduce(lambda l,x: l if x in l else l+[x], rows, [])
        return rows

    def get_ontology(self) -> str:
        ROOT = Namespace('#')
        TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')
        OM = Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
        OMX = Namespace('http://www.foodvoc.org/resource/InternetOfFood/omx/')
        OWL3 = Namespace('http://www.foodvoc.org/resource/InternetOfFood/OntologyWebLanguage/') # BUG IMAGINARY OWL

        og = Graph()
        og.namespace_manager.bind('', ROOT)
        og.namespace_manager.bind('table', TABLE)
        og.namespace_manager.bind('om', OM)
        og.namespace_manager.bind('omx', OMX)
        og.namespace_manager.bind('owl3', OWL3)

        field_names = self.get_field_names()

        og.add((ROOT[self.name], RDF.type, TABLE.DataSchemaClass))
        for field_name in field_names:
            og.add((ROOT[self.name], TABLE.hasColumnProperty, ROOT[field_name]))

        for col_name, col_info in self.column_info.items():
            og.add((ROOT[col_name], RDF.type, TABLE.ColumnProperty))
            og.add((ROOT[col_name], RDFS.domain, ROOT[self.name]))
            og.add((ROOT[col_name], RDFS.range, self._column_type_mapping(col_info['data_type'])))
            og.add((ROOT[col_name], TABLE.hasColumnName, Literal(col_name)))

            ## handle units (only column, TODO fixed/external?)
            if 'unit' in col_info:
                og.add((ROOT[col_name + 'Quantity'], RDF.type, TABLE.InterfaceObjectProperty))
                og.add((ROOT[col_name + 'Quantity'], RDFS.domain, ROOT[self.name]))
                og.add((ROOT[col_name + 'Quantity'], RDFS.range, OM.Quantity))
                # isQuantityPropertyOf
                quantity = BNode()
                og.add((quantity, OMX.hasNumericalValueProperty, ROOT[col_name]))
                og.add((quantity, OMX.hasUnitProperty, ROOT[col_info['unit']]))
                og.add((ROOT[col_name + 'Quantity'], OMX.isQuantityPropertyOf, quantity))
                # value dataTypePropertyChain
                valuePropertyChain = BNode()
                Collection(og, valuePropertyChain, [
                    ROOT[col_name + "Quantity"],
                    OM.hasValue, 
                    OM.hasNumericalValue
                ])
                og.add((ROOT[col_name], OWL3.dataTypePropertyChain, valuePropertyChain))
                # unit dataTypePropertyChain
                unitPropertyChain = BNode()
                Collection(og, unitPropertyChain, [
                    ROOT[col_name + "Quantity"],
                    OM.hasValue, 
                    OM.hasUnit,
                    OM.symbol
                ])
                og.add((ROOT[col_info['unit']], OWL3.dataTypePropertyChain, unitPropertyChain))

            #TODO handle references if required by data source

        return og.serialize(format='turtle')


def get_data_sources(app=None) -> Dict[str, DataSource]:
    global __ds__
    if '__ds__' not in globals():
        if app is None:
            raise ValueError('Flask app required for initialization')
        __ds__ = dict()
        data_source_paths = app.config['DATA_SOURCE_FILE_PATHS']
        ontology_path = app.config['ONTOLOGY_FILE_PATH']
        for data_source_path, column_info in zip(data_source_paths, app.config['COLUMN_TYPES']):
            name = splitext(basename(data_source_path))[0]
            print(name)
            __ds__[name] = DataSource(data_source_path, ontology_path, 
                column_info, name)
    return __ds__
