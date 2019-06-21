import os
import time
import random
from __init__ import *

from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import *
from dota2 import Dota2Client

import logging
#logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

class DotaBotInstance:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.steam = SteamClient()
        self.dota = Dota2Client(self.steam)

        self.steam.on('logged_on', self.on_logged_on)
        self.dota.on('ready', self.on_dota_ready)

        self._login()

    def _login(self):
        #self.username = os.environ['STEAM_BOT_USER']
        #self.password = os.environ['STEAM_BOT_PASS']

        if self.steam.credential_location is None:
            self.steam.set_credential_location(STEAM_CREDENTIAL_STORAGE)
        status = self.steam.login(self.username, password=self.password)

        sentry = self.steam.get_sentry(self.username)
        if sentry:
            self.steam.store_sentry(self.username, self.steam.get_sentry(self.username))
        #self.user = client.user.SteamUser(steam_id, steam)

        if status != EResult.OK:
            print('{}: Login failed returning: {}'.format(self.username, status))

        return status

    def on_logged_on(self):
        print('{}: Login successful!'.format(self.username))
        self.dota.launch()

    def on_dota_ready(self):
        print('Dota ready!')
        if self.dota.lobby:
            self.dota.leave_practice_lobby()
            self.dota.wait_event('lobby_removed')

        #Register callbacks
        self.dota.on('lobby_new', self.on_lobby_new)
        self.dota.on('lobby_changed', self.on_lobby_change)

        self.steam.on('chat_message', self.handle_commands)

        self.create_lobby()

    def on_lobby_new(self, CSODOTALobby):
        #print(CSODOTALobby)
        #self.invite_me_to_party()
        self.invite_me_to_lobby()

    def on_lobby_change(self, CSODOTALobby):
        print(CSODOTALobby)

    def invite_me_to_lobby(self):
        print('Invite {} to lobby'.format(MY_STEAM_ID))
        self.dota.invite_to_lobby(MY_STEAM_ID)

    def invite_me_to_party(self):
        if self.dota.lobby:
            print('Invite {} to party'.format(MY_STEAM_ID))
            self.dota.invite_to_party(MY_STEAM_ID)

    def handle_commands(self, steam_user, msg):
        print(steam_user.name, msg)
        if msg == 'quit':
            DotaBot.instance()._cleanup_clients()
        if msg == 'host':
            self.dota.create_practice_lobby(password='{:3d}'.format(random.randint(0, 999)))
        if msg == 'leavelobby':
            self.dota.leave_practice_lobby()
        if msg == 'party':
            self.dota.invite_to_party(steam_user.steam_id)
        if msg == 'lobby':
            self.dota.invite_to_lobby(steam_user.steam_id)
        if msg == 'status':
            print(self.dota.connection_status)

    def create_lobby(self):
        password = '{:3d}'.format(random.randint(0, 999))

        options = dict({
            'game_name':'{}'.format(self.steam.user.name)
        })

        self.dota.create_practice_lobby(password=password, options=options)

        self.dota.wait_event('lobby_new')
        #self.dota.config_practice_lobby(options)
        print('Lobby: {} | {}'.format(self.dota.lobby.game_name, password))

if __name__ == '__main__':
    passwd = os.environ['STEAM_BOT_PASS']

    unames = ['fairplaybot', 'fairplaybot2']
    bots = [DotaBotInstance(uname, passwd) for uname in unames]

    while True:
        for bot in bots:
            bot.steam.idle()

    #bot1 = DotaBotInstance('fairplaybot', passwd)
    #bot1.steam.run_forever()

    #user_input = input('>')
    #while user_input:
    #    print(user_input)
    #    user_input = input('>')
    #bot2 = DotaBotInstance('fairplaybot1', passwd)
    #bot1 = DotaBotInstance('fairbot1', passwd)

    #bots = [DotaBotInstance(name) for name in ['FairBot1', 'FairBot2', 'FairBot3']]
    #for bot in bots:
    #    bot.create_lobby()
    #bots[0].cl.steam.run_forever()