import os
import psycopg2

DB_NAME = 'postgres'
DB_HOSTNAME = os.environ.get('DB_HOSTNAME', 'localhost')
DB_HOSTPORT = os.environ.get('DB_HOSTPORT', '5432')
DB_USERNAME = 'rss2tg'
DB_PASSWORD = 'rss2tg1234'
DB_DSN = f"user='{DB_USERNAME}' password='{DB_PASSWORD}' dbname='{DB_NAME}' host='{DB_HOSTNAME}' port={DB_HOSTPORT}"

with open('schema.sql', 'r') as schema:
    conn = psycopg2.connect(DB_DSN)
    curs = conn.cursor()
    curs.execute(schema.read())
    conn.commit()
