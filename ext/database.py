import sqlalchemy as sql

server_name = 'servertest'
engine =  sql.create_engine(f"sqlite+pysqlite:////~/Zomboid/db/{server_name}.db", echo=True, future=True)

def connect(f):
    def wrapper():
        with engine.connect() as connection:
            f(con=connection)
    return wrapper

@connect
def get_user(con: sql.engine.Engine, name):
    result = con.execute(sql.text(f'SELECT * FROM whitelist WHERE username = {name}'))
    return result.all()[0]  # return the first result

