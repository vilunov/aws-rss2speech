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

**Prepare the application files**

Compress the `lambda` directory into the `lambda.zip` archive:

```zip lambda.zip -r lambda```


**Deploy the CloudFormation stack**
