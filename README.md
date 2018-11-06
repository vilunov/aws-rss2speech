# rss2speech

**rss2speech** is an AWS-based service for converting RSS-based feeds into
a stream of speech files. It provides Telegram-based 

## Used AWS Technologies

- **CloudFormation**: for easy deployment of the service
- **CloudWatch**: periodically triggering our Lambda
- **Lambda**:
  - checking feeds for new posts
  - triggering Polly
  - saving files to S3 
  - notifying the bot via SQS
- **Polly**: converting text to speech.
- **SQS**: communication between RSS updater and Telegram bot service.
- **S3**: temporary storage of audio files
- **ECS**: hosting of Telegram bot service.

## Deployment Procedure

**Prepare the application files using docker**

```sh
docker build -t rss2tg-lambda lambda
ID=$(docker create rss2tg-lambda /bin/true)
docker cp $ID:/lambda.zip .
docker rm $ID
docker image rm rss2tg-lambda
```


**Deploy the CloudFormation stack**

Create a bucket for storing the application's data:

```sh
AWS_BUCKET=rsstotg
AWS_REGION=us-east-1
aws s3api create-bucket --bucket $AWS_BUCKET --region $AWS_REGION
```

Upload the feed updater code to S3

```sh
aws s3 cp lambda.zip s3://$AWS_BUCKET/lambda.zip
```

Package the stack:

```sh
aws cloudformation package --template stack.yml \
 --region $AWS_REGION --s3-bucket $AWS_BUCKET \
 --output-template-file stack.output.yml
```

And deploy it:

```sh
TG_TOKEN=<token>
TG_ADMIN=<admin_username>
AWS_KEY_NAME=<name_of_your_ssh_key>
aws cloudformation deploy --template-file stack.output.yml \
 --parameter-overrides TelegramToken=$TG_TOKEN \
  AdminTelegramUsername=$TG_ADMIN \
  S3SetupStorage=$AWS_BUCKET \
  InstanceKeyName=$AWS_KEY_NAME \
 --capabilities CAPABILITY_IAM --stack-name rsstotg
```

**Make sure that the stack is deployed properly:**

- Check that the CloudWatch rule is set to trigger the Lambda
- Ensure that the S3 bucket has public access
- Check other services
