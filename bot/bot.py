import logging

from telegram.ext import Updater, CommandHandler

import settings
import handlers

request_kwargs = dict(proxy_url=settings.TG_PROXY) if hasattr(settings, 'TG_PROXY') else {}
updater = Updater(token=settings.TG_TOKEN, request_kwargs=request_kwargs)
dispatcher = updater.dispatcher

handlers = {
    'start': handlers.start,
    'list': handlers.list_all_subscriptions,
    'info': handlers.info,
    'modify': handlers.modify,
    'subscribe': handlers.subscribe,
}

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG)

    for command, handler in handlers.items():
        dispatcher.add_handler(CommandHandler(command, handler))

    updater.start_polling()
