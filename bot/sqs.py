import json
import boto3
from typing import *

import db

sqs = boto3.client('sqs')


def handle_message(bot, msg, conn, users_feeds_cache: Dict[int, List[Tuple[int, Any]]]):
    body = json.loads(msg['Body'])

    filepath: str = body['filepath']
    feed_id: int = body['feed_id']
    text: str = body['text']
    published: str = body['published']

    if feed_id not in users_feeds_cache:
        curs = conn.cursor()
        curs.execute(db.SQL_USERS_BY_RESOURCE_ID, (feed_id,))
        users_feeds_cache[feed_id] = [i for i in curs.fetchall()]
        conn.rollback()
    users: List[(int, Any)] = users_feeds_cache[feed_id]
    print(users)

    for user, s_time in users:
        if published > s_time:
            bot.send_audio(chat_id=user, audio=filepath)
            bot.send_message(chat_id=user, text=text)


def start_fetching(bot, queue_url):
    while True:
        try:
            # Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html
            resp = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20)
            conn = db.connection()
            users_feeds_cache = dict()
            for msg in resp['Messages']:
                handle_message(bot, msg, conn, users_feeds_cache)
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle'])
        except Exception as e:
            print('Exception caught while handling queue messages')
            print(e)
