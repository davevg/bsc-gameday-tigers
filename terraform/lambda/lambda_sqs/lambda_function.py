import boto3
import json
import os
from datetime import datetime

# Initialize clients
sqs = boto3.client('sqs')
s3 = boto3.client('s3')

# Environment variables
QUEUE_URL = os.getenv('QUEUE_URL')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def lambda_handler(event, context):
    try:
        logs = []
        
        # Fetch the current date to structure the S3 path
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        # Get time in hhmmss format
        time_str = now.strftime("%H%M%S")

        while True:
            # Fetch messages from SQS in batches of up to 10
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10  # Receive up to 10 messages at a time
            )
            
            # If no messages are received, break out of the loop
            if 'Messages' not in response:
                break

            # Process each message from SQS
            for message in response['Messages']:
                log_data = json.loads(message['Body'])
                logs.append(log_data)
                # Delete message from the queue after processing
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )

        # Write all logs to S3 if there are any
        if logs:
            # Construct the S3 filename using year/month/day/hhmmss.txt format
            s3_filename = f"logs/{year}/{month}/{day}/{time_str}.csv"
            
            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_filename,
                Body='\n'.join(logs),
                ContentType='text/csv'
            )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Logs written to {s3_filename}, all SQS messages processed")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
