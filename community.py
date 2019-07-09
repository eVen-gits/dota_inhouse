from discord_bot import *
from dota_bot import *
from utils.utils import *

class User:
    PENDING = 'pending'
    VOUCHED = 'vouched'
    TIMEOUT = 'timeout'
    BANNED = 'banned'
    REVIEW = 'review'

    def __init__(self, discord_id=None, steam_id=None, mail=None):
        self.discord_id = discord_id
        self.steam_id = steam_id
        self.mail = mail

    @staticmethod
    @with_db
    def fetch(discord_id=None, steam_id=None, mail=None, conn=None, cursor=None):
        provided = {}
        if discord_id is not None:
            provided['discord_id'] = str(discord_id)
        if steam_id is not None:
            provided['steam_id'] = str(steam_id)
        if mail is not None:
            provided['mail'] = mail

        if not provided:
            raise ArgumentParsingError(
                'Can not fetch player without at least one identifier (discord_id OR steam_id OR mail).'
            )

        kvps = [(k, v) for k, v in provided.items()]

        sql = (
            'SELECT discord_id, steam_id, mail '
            'FROM dbase.player '
            'WHERE {}; '
        ).format(' OR '.join(['{}=%s'.format(kvp[0]) for kvp in kvps]))

        cursor.execute(sql, tuple([kvp[1] for kvp in kvps]))

        result = cursor.fetchone()
        if not result:
            raise KeyError('User {} doesn\'t exist.'.format(', '.join([
                '{}={}'.format(k, v) for k, v in kvps
            ])))

        user = User(result[0], result[1], result[2])

        return user

    @staticmethod
    @with_db
    def fetch_pending(conn=None, cursor=None):
        sql = (
            'SELECT discord_id, steam_id, mail '
            'FROM dbase.player '
            'WHERE status=\'pending\'; '
        )

        cursor.execute(sql)

        results = cursor.fetchall()
        if not results:
            return None

        return [User(discord_id=r[0], steam_id=r[1], mail=r[2]) for r in results]

@with_db
def register_player(discord_id:int, steam_id:int, mail:str, conn=None, cursor=None):
    sql = (
        'INSERT INTO dbase.player '
        '(steam_id, discord_id, mail, status) '
        'VALUES(%s, %s, %s, %s); '
    )
    cursor.execute('BEGIN;')
    cursor.execute(sql, (discord_id, steam_id, mail, User.PENDING))
    cursor.execute('COMMIT;')

def valid_mail(mail):
    return re.match(r"[^@]+@[^@]+\.[^@]+", mail)

def valid_steam_id(steam_id):
    valid = SteamID(steam_id).is_valid()

    #user = SteamUser()

    return valid

def is_new_user(discord_id, steam_id, mail):
    try:
        User.fetch(discord_id=discord_id, steam_id=steam_id, mail=mail)
        return False
    except KeyError as e:
        return True
