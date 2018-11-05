import os

import psycopg2
import psycopg2.extensions


DB_NAME = 'rss2tg'
DB_HOSTNAME = os.environ.get('DB_HOSTNAME', 'localhost')
DB_HOSTPORT = os.environ.get('DB_HOSTPORT', '5432')
DB_USERNAME = 'rss2tg'
DB_PASSWORD = 'rss2tg1234'
DB_DSN = f"user='{DB_USERNAME}' password='{DB_PASSWORD}' dbname='{DB_NAME}' host='{DB_HOSTNAME}' port={DB_HOSTPORT}"

SQL_SUBSCRIPTIONS = (
    'select link from subscriptions s '
    'inner join resources r on s.resource_id = r.id '
    'inner join users u on s.user_id = u.id and u.telegram_id = %s;')

SQL_INFO = (
    'select notifications_on from settings s '
    'inner join users u on s.user_id = u.id and u.telegram_id = %s;')

SQL_ADD_RESOURCE = (
    'insert into resources(link) values (%s) '
    'on conflict (link) do update set link = EXCLUDED.link '
    'returning id;')

SQL_SUBSCRIBE = (
    'insert into subscriptions(user_id, resource_id) '
    'values ((select id from users where telegram_id = %s), %s)'
    'on conflict (user_id, resource_id) do nothing;')

SQL_REGISTER = (
    'insert into users(telegram_id, username) values (%s, %s)'
    'on conflict (telegram_id) do update set username = EXCLUDED.username '
    'returning id;')

SQL_USERS_BY_RESOURCE_ID = (
    'select telegram_id from users u '
    'where u.id in '
    '(select user_id from subscriptions where resource_id = %s);')


def connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(DB_DSN)
