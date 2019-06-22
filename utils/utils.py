import psycopg2
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from utils.config import data as cfg

def db_connect():
    #dbdata = cfg.database
    connstring = 'host={} port={} dbname={} user={} password={}'.format(
        cfg.database.host,
        cfg.database.port,
        cfg.database.database,
        cfg.database.username,
        cfg.database.password)
    conn = psycopg2.connect(connstring)
    cursor = conn.cursor()
    return conn, cursor

def db_disconnect(conn, cursor):
    cursor.close()
    conn.close()

def with_db(func_to_decorate):
    ''' Adds conn and cursor for database connection to keyword args (kwargs).
        If not present, a new connection is made and cleaned up at the end of execution.
        If conn, cursor present in args already, it is passed through without modification.

        The function decorated with this has to have optional kwargs:
        conn=None, cursor=None
    '''
    def wrapper(*original_args, **original_kwargs):
        conn, cursor = None, None
        # If db not connected
        if not original_kwargs.get('conn') or not original_kwargs.get('cursor'):
        # Connect DB
            conn, cursor = db_connect()
            # Add handles to kwargs
            original_kwargs['conn'] = conn
            original_kwargs['cursor'] = cursor

        ret = func_to_decorate(*original_args, **original_kwargs)

        # If new connection was made
        if conn or cursor:
            # Clean DB connections
            db_disconnect(conn, cursor)
        return ret
    return wrapper