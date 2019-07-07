import os
import time
import random
from __init__ import *
from enum import Enum


from dota2.util import replay_url_from_match
from steam.enums import EResult

# Steam GC api
from steam import *
from dota2 import Dota2Client

from utils.utils import *

from tqdm import tqdm

import logging
#logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

class EGameType(Enum):
    RD=0
    CD=1
    CM=2

class BotCredentials:
    def __init__(self, uname, passwd):
        self.uname = uname
        self.passwd = passwd

    @staticmethod
    @with_db
    def fetch_all(conn=None, cursor=None):
        sql = (
            'SELECT username, pass '
            'FROM dbase.bot '
        )
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            raise KeyError('No bot credentials stored in the database.')
        return [BotCredentials(uname, pwd) for uname, pwd in results]

class DotaBotCluster:
    def __init__(self, wait_dota=True):
        self.bots = []
        self._init_bots(wait_dota=wait_dota)

    def _init_bots(self, wait_dota=True):
        bot_credentials = BotCredentials.fetch_all()
        print('Launching bots...')
        self.bots = [
            DotaBotInstance(cred.uname, cred.passwd, wait_dota=wait_dota)
            for cred in
            tqdm(bot_credentials)
        ]

    def idle(self):
        for bot in self.bots:
            bot.idle()

    def run_forever(self, freq=0.1):
        if len(self.bots) < 1:
            return
        while True:
            self.idle()
            time.sleep(freq)

class DotaBotInstance:
    def __init__(self, username, password, wait_dota=True):
        self.username = username
        self.password = password

        self.steam = SteamClient()
        self.dota = Dota2Client(self.steam)

        self.steam.on('logged_on', self.on_logged_on)
        self.dota.on('ready', self.on_dota_ready)

        self._login(wait_dota)

    @property
    def name(self):
        if not self.steam.logged_on:
            return 'None'
        return self.steam.user.name

    def _login(self, wait_dota=True):
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
        if wait_dota:
            self.dota.wait_event('ready')
        return status

    def idle(self):
        self.steam.idle()

    def on_logged_on(self):
        #print('{}: Login successful!'.format(self.username))
        self.dota.launch()

    def on_dota_ready(self):
        #print('Dota ready!')wait_dota
        if self.dota.lobby:
            self.dota.leave_practice_lobby()
            self.dota.wait_event('lobby_removed')

        #Register callbacks
        self.dota.on('lobby_new', self.on_lobby_new)
        self.dota.on('lobby_changed', self.on_lobby_change)

        self.steam.on('chat_message', self.handle_commands)

    def on_lobby_new(self, CSODOTALobby):
        #print(CSODOTALobby)
        #self.invite_me_to_party()
        #self.invite_me_to_lobby()
        self.dota.join_practice_lobby_broadcast_channel()

    def on_lobby_change(self, CSODOTALobby):
        print(self.name)

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
    cluster = DotaBotCluster()
    cluster.run_forever()