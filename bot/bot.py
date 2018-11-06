import logging

from telegram.ext import Updater, CommandHandler

import settings
import handlers
import sqs

request_kwargs = dict(proxy_url=settings.TG_PROXY) if hasattr(settings, 'TG_PROXY') else {}
updater = Updater(token=settings.TG_TOKEN, request_kwargs=request_kwargs)
dispatcher = updater.dispatcher

handlers_dict = {
    'start': handlers.start,
    'list': handlers.list_all_subscriptions,
    'info': handlers.info,
    'modify': handlers.modify,
}

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG)

    for command, handler in handlers_dict.items():
        dispatcher.add_handler(CommandHandler(command, handler))
    dispatcher.add_handler(CommandHandler('subscribe', handlers.subscribe, pass_args=True))

    queue = updater.start_polling()
    while True:
        try:
            sqs.start_fetching(updater.bot, settings.AWS_SQS_URL)
        except Exception as e:
            print('Exception high level')
            print(e, type(e))
