def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def list_all_subscriptions(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="List of all your subscriptions: []")


def info(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Settings for your subscription: []")


def modify(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You successfully modified setting for your subscription!")


def subscribe(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You successfully subscribed for feed!")


def new_post(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="New post has arrived")
