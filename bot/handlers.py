from bot import *
import psycopg2

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def list_all_subscriptions(bot, update):
    conn = psycopg2.connect(DB_DSN)

    curs = conn.cursor()
    curs.execute("""
                    SELECT link;
                      FROM subscriptions s
                      
                INNER JOIN resources r 
                        ON s.resource_id = r.id
                
                INNER JOIN users u
                        ON s.user_id = u.id 
                       AND u.telegram_id = %s
                """, update.message.chat_id)

    bot.send_message(chat_id=update.message.chat_id, text=f"List of your subscriptions: <br>"
                                                          f"{'<br>'.join(['- '+ link[0] for link in curs])}")

    conn.rollback()


def info(bot, update):
    conn = psycopg2.connect(DB_DSN)

    curs = conn.cursor()
    curs.execute("""
                    SELECT notifications_on
                      FROM settings
                    
                INNER JOIN users u 
                        ON s.user_id = u.id
                       AND u.telegram_id = %s
                """, update.message.chat_id)

    user_settings = curs[0]
    bot.send_message(chat_id=update.message.chat_id, text=f"Settings for your subscription: "
                                                          f"- Notifications On: {user_settings[0]}")

    conn.rollback()


def modify(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You successfully modified setting for your subscription!")


def subscribe(bot, update, args):
    conn = psycopg2.connect(DB_DSN)
    link = args[0]

    curs = conn.cursor()

    curs.execute("""
              INSERT INTO resources(link)
                   VALUES (%s)
              ON CONFLICT (link) DO 
               UPDATE SET link = EXCLUDED.link
                RETURNING id;
                """, link)

    id = curs[0][0]

    curs.execute("""
                    INSERT INTO subscriptions(user_id, resource_id)
                         VALUES (%s, %s)
                    ON CONFLICT (user_id, resource_id) DO NOTHING
                """, update.messag.chat_id, id)

    bot.send_message(chat_id=update.message.chat_id, text="You successfully subscribed for feed!")

    conn.commit()


def new_post(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="New post has arrived")
