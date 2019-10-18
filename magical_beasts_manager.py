import os
import random as rnd
import json


root_dir_path = os.path.dirname(os.path.abspath(__file__))

magical_beasts_jsons_path = root_dir_path + "/Resources/Magical_Beasts/JSONS"
magical_beasts_images_path = root_dir_path + "/Resources/Magical_Beasts/Images"

magical_beasts_jsons = os.listdir(magical_beasts_jsons_path)


class MagicalBeast:

    def __init__(self, magical_beast_json_path):
        self.json = magical_beast_json_path
        with open(self.json, 'r') as file:
            file_data = file.read()
        self.data = json.loads(file_data)

    def get_data(self):
        return self.data


def get_random_magical_beast():
    magical_beast_file_path = magical_beasts_jsons_path + "/" + rnd.choice(magical_beasts_jsons)
    return MagicalBeast(magical_beast_file_path)


def get_magical_beast_by_kind(kind):
    path = magical_beasts_jsons_path + "/" + kind + ".json"
    if not os.path.isfile(path):
        return None
    return MagicalBeast(path)


def get_magical_beast_uri(magical_beast):
    return "{0}/{1}".format(magical_beasts_images_path, magical_beast.get_data()["uri"])
