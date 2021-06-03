from typing import List, Tuple, Dict
from functools import reduce
import csv
from os.path import splitext, basename

from rdflib import Namespace, RDF, RDFS, XSD
from rdflib.term import URIRef, Literal
from rdflib.graph import Graph

class DataSource:
    def __init__(self, data_path, ontology_path, column_types, name):
        self.data_path = data_path
        self.ontology_path = ontology_path
        self.column_types = column_types

        self.name = name
        self.id = None

    def get_field_names(self) -> List[str]:
        fields = list()
        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)
            fields = reader.fieldnames
        return fields

    def get_column_types(self) -> Dict[str, type]:
        return self.column_types

    def _column_type_mapping(self, type) -> URIRef:
        return XSD[type.__name__.lower()]

    def get_rows(self, columns: Tuple[str, ...], unique: bool) -> List[dict]:

        rows = list()

        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)

            for line in reader:
                rows.append({key: self.column_types[key](line[key]) for key in columns})
            
            if unique:
                rows = reduce(lambda l,x: l if x in l else l+[x], rows, [])
        return rows

    def get_ontology(self) -> str:
        ROOT = Namespace('#')
        TABLE = Namespace('http://www.foodvoc.org/resource/InternetOfFood/Table/')

        og = Graph()
        og.namespace_manager.bind('', ROOT)
        og.namespace_manager.bind('table', TABLE)

        field_names = self.get_field_names()
        field_types = self.get_column_types()

        og.add((ROOT[self.name], RDF.type, TABLE.DataTableClass))
        for field_name in field_names:
            og.add((ROOT[self.name], TABLE.hasColumnProperty, ROOT[field_name]))

        for col_name, col_type in field_types.items():
            og.add((ROOT[col_name], RDF.type, TABLE.ColumnProperty))
            og.add((ROOT[col_name], RDFS.domain, ROOT[self.name]))
            og.add((ROOT[col_name], RDFS.range, self._column_type_mapping(col_type)))
            og.add((ROOT[col_name], TABLE.hasColumnName, Literal(col_name)))

        # TODO load and add external ontology definition
        # ... or add external data source references + value*unit definitions to code or config
        #       open(self.ontology_path, 'rt').readlines())])

        return og.serialize(format='turtle')


def get_data_sources(app=None) -> Dict[str, DataSource]:
    global __ds__
    if '__ds__' not in globals():
        if app is None:
            raise ValueError('Flask app required for initialization')
        __ds__ = dict()
        data_source_paths = app.config['DATA_SOURCE_FILE_PATHS']
        all_column_types = [{c: eval(t) for c,t in ct.items()} for ct in app.config['COLUMN_TYPES']]
        ontology_path = app.config['ONTOLOGY_FILE_PATH']
        for data_source_path, column_types in zip(data_source_paths, all_column_types):
            name = splitext(basename(data_source_path))[0]
            print(name)
            __ds__[name] = DataSource(data_source_path, ontology_path, 
                column_types, name)
    return __ds__
