from typing import List, Union, Tuple
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
    def __init__(self, data_path, ontology_path):
        self.data_path = data_path
        self.ontology_path = ontology_path

    def get_field_names(self) -> List[str]:
        fields = list()
        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)
            fields = reader.fieldnames
        return fields

    def get_rows(self, columns: Tuple[str, ...], unique: bool) -> List[dict]:

        rows = list()

        with open(self.data_path, 'rt') as source_csv:
            reader = csv.DictReader(source_csv)

            for line in reader:
                rows.append({key: line[key] for key in columns})
            
            if unique:
                rows = reduce(lambda l,x: l if x in l else l+[x], rows, [])
        return rows

    def get_ontology(self) -> str:
        return "".join(open(self.ontology_path, 'rt').readlines())


def get_data_sources(app=None) -> DataSource:
    global __ds__
    if '__ds__' not in globals():
        if app is None:
            raise ValueError('Flask app required for initialization')
        __ds__ = dict()
        for data_source_path, ontology_path in zip(app.config['DATA_SOURCE_FILE_PATHS'], app.config['ONTOLOGY_FILE_PATHS']):
            index = splitext(basename(data_source_path))[0]
            print(index)
            __ds__[index] = DataSource(data_source_path, ontology_path)
    return __ds__
