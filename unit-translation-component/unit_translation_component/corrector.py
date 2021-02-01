from spellchecker import SpellChecker
import os


class SpellCheckerObject:
    __instance = None
    __flag = None

    @staticmethod
    def get_instance():
        if SpellCheckerObject.__instance is None:
            SpellCheckerObject()
        return SpellCheckerObject.__instance

    def __init__(self):
        if SpellCheckerObject.__instance is not None:
            raise Exception("This is a singleton class.")
        else:
            path = os.path.abspath(__file__)
            path = path[:-12]
            path = path + 'unit_dictionary.json'
            SpellCheckerObject.__instance = SpellChecker(language=None, distance=4, case_sensitive=True)
            SpellCheckerObject.__instance.word_frequency.load_dictionary(path)

    @staticmethod
    def path():
        path = os.path.abspath(__file__)
        path = path[:-12]
        path = path + 'unit_dictionary.json'
        return path
