import json
import boto3
import os

sns = boto3.client('sns')
TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            message = f"New invoice inserted: {json.dumps(new_image)}"
            
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject='New Invoice Notification'
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Notifications sent successfully')
    }