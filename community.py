from discord_bot import *
from dota_bot import *
from utils.utils import *

class User:
    PENDING = 'pending'
    VOUCHED = 'vouched'
    TIMEOUT = 'timeout'
    BANNED = 'banned'
    REVIEW = 'review'

    def __init__():
        pass

    @staticmethod
    @with_db
    def fetch(internal_id=None, discord_id=None, steam_id=None, conn=None, cursor=None):
        sql = (
            'SELECT column_name '
            'FROM information_schema.columns '
            'WHERE table_schema = \'{}\' '
            'AND table_name = \'mast\' '
        ).format(project.sname)

        cursor.execute(sql)
        result = cursor.fetchall()

        columns = [r[0] for r in result]

        sql = (
            'SELECT {} '
            'FROM {}.mast '
            'WHERE id=%s; '
        ).format(', '.join(columns), project.sname)

        cursor.execute(sql, (m_id,))

        result = cursor.fetchone()
        if not result:
            raise KeyError('Event {} not in {} schema.'.format(evt_id, project.sname))

        datadict = dict()
        i=0

        for col in columns:
            datadict[col] = result[i]
            i = i+1

        return MastInfo(datadict, project)

@with_db
def register_player(discord_id:int, steam_id:int, email:str, conn=None, cursor=None):
    sql = (
        'INSERT INTO dbase.player '
        '(steam_id, discord_id, mail, status) '
        'VALUES(%s, %s, %s, %s); '
    )
    cursor.execute('BEGIN;')
    cursor.execute(sql, (discord_id, steam_id, email, User.PENDING))
    cursor.execute('COMMIT;')

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def valid_steam_id(steam_id):
    valid = SteamID(steam_id).is_valid()

    #user = SteamUser()

    return valid