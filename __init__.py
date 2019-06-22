from os import environ as env
from os import path

from steam import SteamID

#import gevent.monkey
#gevent.monkey.patch_all()

try:
    MY_STEAM_ID = SteamID(int(env['MY_STEAM_ID']))
except Exception:
    MY_STEAM_ID = None

STEAM_CREDENTIAL_STORAGE = path.join(path.dirname(path.realpath(__file__)), 'steam_credentials')