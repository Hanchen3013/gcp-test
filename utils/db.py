import sqlalchemy
import os

def get_engine():
    return sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
        )
    )

def insert_to_sql(table, transcript_id, text):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            f"INSERT INTO {table} (transcript_id, text) VALUES (%s, %s)",
            (transcript_id, text)
        )
