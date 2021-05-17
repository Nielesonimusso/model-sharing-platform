from typing import List, Union, Tuple, Dict
from functools import reduce
import csv
from flask import Flask
from os.path import splitext, basename

class IngredientProperty:

    def __init__(self, ingredient: str, ingredient_code: str, ingredient_property: str, 
            value_text: str, value_num: Union[int, float], unit_of_measure: str):
        self.ingredient = ingredient
        self.ingredient_code = ingredient_code
        self.ingredient_property = ingredient_property
        self.value_text = value_text
        self.value_num = value_num
        self.unit_of_measure = unit_of_measure

    def __eq__(self, other):
        return (self.ingredient == other.ingredient and 
            self.ingredient_code == other.ingredient_code and
            self.ingredient_property == other.ingredient_property and
            self.value_text == other.value_text and
            (self.value_num - other.value_num <= 0.0001) and
            self.unit_of_measure == other.unit_of_measure)


class DataSource:
    def __init__(self, data_path, ontology_path, column_types, name, ontology_prefix):
        self.data_path = data_path
        self.ontology_path = ontology_path
        self.column_types = column_types

        self.name = name
        self.ontology_prefix = ontology_prefix

    def get_field_names(self) -> List[str]:
        fields = list()
        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)
            fields = reader.fieldnames
        return fields

    def get_column_types(self) -> Dict[str, type]:
        return self.column_types

    def _column_type_mapping(self, type):
        return {str: "xsd:string", float: "xsd:double"}[type]

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

        field_names = self.get_field_names()
        field_types = self.get_column_types()

        prefix_def = f"""@prefix table:urn:....
@prefix {self.ontology_prefix}:urn:....

"""

        table_def = f"""### Representation Model ###

{self.ontology_prefix}:{self.name}Table a table:DataTableClass;
"""
        table_col_def = ";\n".join(
            [f"   table:hasColumnProperty {self.ontology_prefix}:{field_name}"
                 for field_name in field_names]) + """.

"""

        cols_defs = "".join([f"""{self.ontology_prefix}:{col_name} a table:ColumnProperty
    rdfs:domain {self.ontology_prefix}:{self.name};
    rdfs:range {self._column_type_mapping(col_type)};
    table:hasColumnName \"{col_name}\".

""" for col_name, col_type in field_types.items()])

        return "".join([prefix_def, table_def, table_col_def, cols_defs, 
        """### Conceptual Model ###

""",
            "".join(open(self.ontology_path, 'rt').readlines())])


def get_data_sources(app=None) -> Dict[str, DataSource]:
    global __ds__
    if '__ds__' not in globals():
        if app is None:
            raise ValueError('Flask app required for initialization')
        __ds__ = dict()
        data_source_paths = app.config['DATA_SOURCE_FILE_PATHS']
        all_column_types = app.config['COLUMN_TYPES']
        ontology_path = app.config['ONTOLOGY_FILE_PATH']
        ontology_prefix = app.config['ONTOLOGY_PREFIX']
        for data_source_path, column_types in zip(data_source_paths, all_column_types):
            name = splitext(basename(data_source_path))[0]
            print(name)
            __ds__[name] = DataSource(data_source_path, ontology_path, 
                column_types, name, ontology_prefix)
    return __ds__
