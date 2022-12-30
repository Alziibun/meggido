import sqlalchemy as sql

server_name = 'servertest'
engine =  sql.create_engine(f"sqlite+pysqlite:////home/pzuser/Zomboid/db/{server_name}.db", echo=True, future=True)

def connect(f):
    def wrapper(*args, **kwargs):
        with engine.connect() as connection:
            result = f(con=connection, *args, **kwargs)
            return result
    return wrapper

@connect
def get_user(con: sql.engine.Engine, *, name: str=""):
    result = con.execute(sql.text(f'SELECT * FROM whitelist WHERE username = "{name}"')).fetchone()
    if result is not None: result = result._asdict()
    print(result)
    return result  # return the first result

