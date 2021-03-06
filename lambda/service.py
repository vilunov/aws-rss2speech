import os
import dateutil.parser
import json
from datetime import datetime
from contextlib import closing
from typing import *

import boto3
from botocore.exceptions import BotoCoreError
import feedparser
import psycopg2
import bs4


DB_NAME = 'rss2tg'
DB_HOSTNAME = os.environ.get('DB_HOSTNAME')
DB_HOSTPORT = os.environ.get('DB_HOSTPORT', '5432')
DB_USERNAME = 'rss2tg'
DB_PASSWORD = 'rss2tg1234'
DB_DSN = f"user='{DB_USERNAME}' password='{DB_PASSWORD}' dbname='{DB_NAME}' host='{DB_HOSTNAME}' port={DB_HOSTPORT}"

DB_QUERY_FEEDS = 'select id, link from resources where id in (select resource_id from subscriptions);'
DB_QUERY_GET_PROCESSED = 'select 1 from processed_posts where resource_id = %s and post_filename = %s;'
DB_QUERY_SET_PROCESSED = 'insert into processed_posts(resource_id, post_filename) values(%s, %s);'

MAX_TPS = 10
MAX_CONCURENT_CONNECTIONS = 20
TASKS = 100
REQUEST_LIMIT = 1200

TEXT_NEW_POST = u"""New post, author {author}, title {title}."""

AWS_BUCKET = os.environ.get('AWS_BUCKET')
AWS_SQS_QUEUE_URL = os.environ.get('AWS_SQS_QUEUE_URL')


messages = 0


def get_feeds_urls(conn) -> List[Tuple[int, str]]:
    """
    Get all feeds with subscriptions
    :return: iterator of feed ids and urls
    """
    curs = conn.cursor()
    curs.execute(DB_QUERY_FEEDS)
    feeds = list(curs)
    conn.rollback()

    return feeds


def split_content_by_dot(soup, max_len):
    """
    split HTML soup into parts not bigger than max_len may break prosody where
    dot is not at the end of the sentence (like "St. Louis") in some cases may
    be synthesized as two separate sentences
    """
    text = soup.get_text(" ", strip=True)
    start = 0
    while start < len(text):
        if len(text) - start <= max_len:
            yield text[start:]
            return
        max = start + max_len
        index = text.rfind(".", start, max)
        if index == start:
            start += 1
        elif index < 0:
            yield text[start:max + 1]
            start = max + 1
        else:
            yield text[start:index + 1]
            start = index + 1


def get_entries(feed) -> Iterator[dict]:
    """
    Extract entries from feed
    :param feed: feed as returned by feedparser
    :return: iterator of dictionaries
    """
    for entry in feed.entries:
        entry_content = entry.content[0].value
        soup = bs4.BeautifulSoup(entry_content, 'html.parser')
        chunks = split_content_by_dot(soup, REQUEST_LIMIT)
        published = dateutil.parser.parse(entry.published)
        date_str = str(published.timestamp())
        entry_id = entry.id + '_' + date_str
        entry_id = ''.join(i for i in entry_id if i.isalnum())
        yield dict(
            content=TEXT_NEW_POST.format(author=entry.author, title=entry.title),
            id=entry_id + '_' + '0',
            title=entry.title,
            published=published,
        )
        for i, chunk in enumerate(chunks):
            yield dict(
                content=chunk,
                id=entry_id + '_' + str(i + 1),
                title=entry.title,
                published=published,
            )


def is_processed(conn, feed_id, filename):
    curs = conn.cursor()
    curs.execute(DB_QUERY_GET_PROCESSED, (feed_id, filename))
    r = bool(curs.fetchone())
    conn.rollback()
    return r


def set_processed(conn, feed_id, filename):
    curs = conn.cursor()
    curs.execute(DB_QUERY_SET_PROCESSED, (feed_id, filename))
    conn.commit()


def handle_entry(entry, feed_id, polly, bucket, sqs, bucket_url, conn):
    """
    Converts an entry to speech and uploads the audio file to S3
    """
    global messages
    filename = f"{feed_id}/{entry['id']}.mp3"

    if is_processed(conn, feed_id, entry['id']):
        print(
            f"Article \"{entry['title']}\" with id {entry['id']} already exist, skipping")
        return

    try:
        print(f"Next entry, size: {len(entry['content'])}")
        response = polly.synthesize_speech(
                Text=entry['content'], OutputFormat='mp3', VoiceId='Joanna')
        with closing(response["AudioStream"]) as stream:
            bucket.put_object(Key=filename, Body=stream.read())

        message = dict(
            filepath=bucket_url + filename,
            feed_id=feed_id,
            text=entry['content'],
            published=int(entry['published'].timestamp()))
        sqs.send_message(QueueUrl=AWS_SQS_QUEUE_URL, MessageBody=json.dumps(message))
        messages += 1
    except BotoCoreError as error:
        print('Error:', error)
        return

    set_processed(conn, feed_id, entry['id'])


def handler(event, context):
    global messages
    polly = boto3.client('polly')
    s3 = boto3.resource('s3')
    sqs = boto3.client('sqs')
    bucket_url = f"https://s3.amazonaws.com/{AWS_BUCKET}/"
    conn = psycopg2.connect(DB_DSN)

    bucket = s3.Bucket(AWS_BUCKET)

    for feed_id, url in get_feeds_urls(conn):
        try:
            feed = feedparser.parse(url)
            for entry in get_entries(feed):
                handle_entry(entry, feed_id, polly, bucket, sqs, bucket_url, conn)
        except Exception as e:
            print('Exception caught while parsing a feed', url)
            print(e, type(e))
    print('Messages sent to SQS:', messages)
