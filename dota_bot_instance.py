import os
import time
import random

from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import *
from dota2 import Dota2Client

import logging

class DotaBotInstance:
    def __init__(self, name='DefaultBot'):
        self.name = name

        self.steam = SteamClient()
        self.dota = Dota2Client(self.steam)

        self.on_logged_on = self.steam.on('logged_on')(self.on_logged_on)

        self._login()

    def _login(self):
        user = os.environ['STEAM_BOT_USER']
        password = os.environ['STEAM_BOT_PASS']

        if self.steam.credential_location is None:
            self.steam.set_credential_location(os.path.dirname(os.path.realpath(__file__)))
        self.steam.get_sentry(user)
        status = self.steam.login(user, password=password)
        self.steam.store_sentry(user, self.steam.get_sentry(user))

        if status != EResult.OK:
            print('Login failed returning: ', status)
        else:
            print('Login successful!')
        return status

    #@steam.on('logged_on')
    def on_logged_on(self):
        self.dota.launch()
        self.dota.wait_event('ready')
        print(self.name)

    def create_lobby(self):
        password = '{:3d}'.format(random.randint(0, 999))
        self.dota.create_practice_lobby(password=password)
        self.dota.config_practice_lobby({
            'game_name':self.name
        })
        print('Lobby: {} | {}'.format(self.name, password))
        #self.cl.dota.invite_to_lobby(95251565)

if __name__ == '__main__':
    bot = DotaBotInstance('FairBot')
    bot.steam.run_forever()
    #bots = [DotaBotInstance(name) for name in ['FairBot1', 'FairBot2', 'FairBot3']]
    #for bot in bots:
    #    bot.create_lobby()
    #bots[0].cl.steam.run_forever()