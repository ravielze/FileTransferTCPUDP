import json

CONFIG = dict()
with open('config.json', 'r') as configFile:
    CONFIG = json.load(configFile)
