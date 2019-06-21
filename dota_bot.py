import os
import time
import random

from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import *
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
        user = os.environ['STEAM_BOT_USER']
        password = os.environ['STEAM_BOT_PASS']

        if cl_steam.credential_location is None:
            cl_steam.set_credential_location(os.path.dirname(os.path.realpath(__file__)))
        cl_steam.get_sentry(user)
        status = cl_steam.login(user, password=password)
        cl_steam.store_sentry(user, cl_steam.get_sentry(user))

        if status != EResult.OK:
            print('Login failed returning: ', status)
        else:
            print('Login successful!')
        return status

    @cl_dota2.on('ready')
    def dota_ready():
        print('Dota ready!')
        DotaBot.instance().dota2_ready = True
        cl_steam.games_played([cl_dota2.app_id])

        #TODO: Rich presence
        #cl_steam.change_status(
        #    persona_state_flags=
        #        enums.common.EPersonaStateFlag.HasRichPresence | enums.common.EPersonaStateFlag.Online
        #)
        #print(DotaBot.instance().steam.user.rich_presence)

    @cl_steam.on('logged_on')
    def _launch_dota():
        DotaBot.instance().dota.launch()
        DotaBot.instance().dota.wait_event('ready')

    @cl_dota2.on('party_invite')
    def accept_party_invite(message):
        print(message)
        DotaBot.instance().dota.respond_to_party_invite(message.group_id, accept=True)

    @cl_steam.on("chat_message")
    def print_message(steam_user, msg):
        print(steam_user.name, msg)
        if msg == 'quit':
            DotaBot.instance()._cleanup_clients()
        if msg == 'host':
            DotaBot.instance().dota.create_practice_lobby(password='{:3d}'.format(random.randint(0, 999)))
        if msg == 'leavelobby':
            DotaBot.instance().dota.leave_practice_lobby()
        if msg == 'party':
            DotaBot.instance().dota.invite_to_party(steam_user.steam_id)
        if msg == 'lobby':
            DotaBot.instance().dota.invite_to_lobby(steam_user.steam_id)
        if msg == 'status':
            print(DotaBot.instance().dota.connection_status)
        return

    def _init_clients(self):
        #logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
        cl_dota2.verbose_debug = True

        self._login()
        #self._launch_dota()

    def _cleanup_clients(self):
        cl_dota2.exit()
        cl_steam.emit('finished')
        cl_steam.logout()
        cl_steam.disconnect()
        quit()

    def __enter__(self):
        self._init_clients()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup_clients()

if __name__ == '__main__':
    with DotaBot() as bot:
        bot.steam.run_forever()
        print('Hello')
    #my_client.steam_wait('chat_message')
    #my_client.steam_client.run_forever()