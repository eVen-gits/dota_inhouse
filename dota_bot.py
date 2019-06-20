from os import environ as environment
import time

from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import SteamClient
from dota2 import Dota2Client

import logging


cl_steam = SteamClient()
cl_dota2 = Dota2Client(cl_steam)


class DotaBot:
    __instance = None

    @staticmethod
    def instance():
        """ Static access method. """
        if DotaBot.__instance == None:
            DotaBot()
        return DotaBot.__instance

    def __init__(self):
        if DotaBot.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DotaBot.__instance = self
        self.dota = cl_dota2
        self.steam = cl_steam

    def _login(self):
        user = environment['STEAM_BOT_USER']
        password = environment['STEAM_BOT_PASS']

        status = cl_steam.cli_login(username=user, password=password)

        if status != EResult.OK:
            print('Login failed returning: ', status)
        else:
            print('Login successful!')
        return status

    @cl_dota2.on('ready')
    def dota_ready():
        print('Dota ready!')
        DotaBot.instance().dota2_ready = True
        cl_steam.games_played ([cl_dota2.app_id])

    @cl_dota2.on('party_invite')
    def accept_party_invite(message):
        print(message)
        DotaBot.instance().dota.respond_to_party_invite(message.group_id, accept=True)

    @cl_steam.on("chat_message")
    def print_message(steam_user, msg):
        print(steam_user.name, msg)
        if msg == 'quit':
            DotaBot.instance()._cleanup_clients()
        elif msg == 'host':
            DotaBot.instance().dota.create_practice_lobby(password='')
        elif msg == 'party':
            DotaBot.instance().dota.invite_to_party(steam_user.steam_id)
        elif msg == 'lobby':
            DotaBot.instance().dota.invite_to_lobby(steam_user.steam_id)

    def _init_clients(self):
        logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)


        while not cl_steam.connected:
            if not cl_steam.reconnect(maxdelay=1, retry=0):
                print('Failed to connect, reattempting...')

        self._login()
        self._launch_dota()

    def _launch_dota(self):
        self.dota.launch()
        self.dota.wait_event('ready')

    def _cleanup_clients(self):
        cl_dota2.exit()
        cl_steam.emit('finished')
        cl_steam.logout()
        cl_steam.disconnect()

    def __enter__(self):
        self._init_clients()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup_clients()

if __name__ == '__main__':
    with DotaBot() as bot:
        bot.steam.run_forever()
    #my_client.steam_wait('chat_message')
    #my_client.steam_client.run_forever()