from os import environ as environment

from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import SteamClient
from dota2 import Dota2Client

import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)


steam_client = SteamClient()
dota2_client = Dota2Client(steam_client)

# api_usage_path = Path('../data/api.json')
# if api_usage_path.is_file():
#     with open(api_usage_path, 'r') as file:
#         api_usage = load(file)

WEB_API_LIMIT = 100000
# Unkown if it is this low, reported by dota2 docs.
GC_API_LIMIT = 100


def gc_login():
    user = environment['STEAM_BOT_USER']
    password = environment['STEAM_BOT_PASS']

    status = steam_client.cli_login(user, password)

    if status != EResult.OK:
        print('Login failed returning: ', status)
    else:
        print('Login successful!')


class SingleDotaClient(object):
    __instance = None

    def __new__(cls, token):
        if SingleDotaClient.__instance is None:
            SingleDotaClient.__instance = object.__new__(cls)

            SingleDotaClient.__instance.token = token
            SingleDotaClient.__instance.dota2_client = dota2_client
            SingleDotaClient.__instance.steam_client = steam_client
            SingleDotaClient.__instance.dota2_ready = False
            gc_login()

        return SingleDotaClient.__instance

    @steam_client.on('logged_on')
    def __start_dota():
        print('Launching dota 2 game controller.')
        SingleDotaClient.__instance.dota2_client.launch()
        SingleDotaClient.__instance.dota2_client.emit('dota2_ready')
        SingleDotaClient.__instance.steam_client.wait_event('finished')

    @dota2_client.on('ready')
    def __dota_ready():
        SingleDotaClient.__instance.dota2_ready = True
        print('Dota ready!')

    @dota2_client.on("match_details")
    def emit_replay_id(replay_id, eresult, replay):
        url = replay_url_from_match(replay)
        SingleDotaClient.__instance.dota2_client.emit("replay_url", replay_id, url)

    @steam_client.on("chat_message")
    def print_message(steam_user, msg):
        print(msg)
        SingleDotaClient.__instance.close()

    def close(cls):
        SingleDotaClient.__instance.steam_client.emit('finished')
        SingleDotaClient.__instance.dota2_ready = False
        SingleDotaClient.__instance.dota2_client.exit()
        SingleDotaClient.__instance.steam_client.disconnect()

    def dota_wait(cls, *args, **kwargs):
        return SingleDotaClient.__instance.dota2_client\
                               .wait_event(*args, **kwargs)

    def steam_wait(cls, *args, **kwargs):
        return SingleDotaClient.__instance.steam_client\
                               .wait_event(*args, **kwargs)

if __name__ == '__main__':
    my_client = SingleDotaClient('token')
    my_client.steam_wait('chat_message')