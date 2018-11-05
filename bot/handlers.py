import psycopg2

from db import *


def start(bot, update):
    conn = psycopg2.connect(DB_DSN)

    curs = conn.cursor()
    curs.execute(SQL_REGISTER, (update.message.chat_id, update.message.from_user.username,))
    conn.commit()

    bot.send_message(chat_id=update.message.chat_id, text="Welcome to Podcast Bot!")


def list_all_subscriptions(bot, update):
    conn = psycopg2.connect(DB_DSN)

    curs = conn.cursor()
    curs.execute(SQL_SUBSCRIPTIONS, (update.message.chat_id,))

    text = 'List of your subscriptions:\n' + ('\n'.join('- ' + link[0] for link in curs) or 'none')
    bot.send_message(chat_id=update.message.chat_id, text=text)

    conn.rollback()


def info(bot, update):
    conn = psycopg2.connect(DB_DSN)

    curs = conn.cursor()
    curs.execute(SQL_INFO, (update.message.chat_id,))
    user_settings = curs.fetchone()
    conn.rollback()

    if user_settings:
        text = (
            f"Settings for your subscription:\n"
            f"- Notifications On: {user_settings[0]}")
    else:
        text = 'No settings stored for you, sorry'

    bot.send_message(chat_id=update.message.chat_id, text=text)


def modify(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You successfully modified setting for your subscription!")


def subscribe(bot, update, args):
    conn = psycopg2.connect(DB_DSN)
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Specify only one argument ples')
        return

    link = args[0]

    curs = conn.cursor()
    curs.execute(SQL_ADD_RESOURCE, (link,))

    resource_id = curs.fetchone()[0]

    curs.execute(SQL_SUBSCRIBE, (update.message.chat_id, resource_id))
    conn.commit()

    bot.send_message(chat_id=update.message.chat_id, text="You successfully subscribed for feed!")


def new_post(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="New post has arrived")
