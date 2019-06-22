import json
import os
from utils.jsonobject import Json2Obj

with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    #data = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    #data = data._replace(paths=data.paths._replace(skytek_root=os.getcwd()))
    data = Json2Obj(json.load(f))
    data.database.password = os.environ['FAIRPLAY_DBASE_PASS']
