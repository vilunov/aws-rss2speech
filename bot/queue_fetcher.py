import boto3

sqs = boto3.client('sqs')


def handle_message(bot, msg):
    # TODO message parsing (deserialization)
    body = msg['Body']
    bot.send_message(chat_id=body.chat_id, text=body.post)
    # TODO think about how to serve audio file. send_audio can accept source URL for automatic downloading
    bot.send_audio(chat_id=body.chat_id, audio=body.audio_url)


def start_fetching(bot, queue_url):
    while True:
        # Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html
        resp = sqs.receive_messages(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=10,
            WaitTimeSeconds=120)

        for msg in resp['Messages']:
            handle_message(bot, msg)
