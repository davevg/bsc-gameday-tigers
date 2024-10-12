import json
import boto3
import logging
import os
import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
bucket_name = os.getenv('S3_BUCKET_NAME', 'bsc-2024-gameday-tigers')  # Add your bucket name

# Initialize S3 client
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    try:
        # The payload is passed as a single log entry
        log = event['log_message']  # Extract the log message from event

        dt_object = datetime.datetime.fromtimestamp(log['timestamp'])
        year, month, day = dt_object.year, dt_object.month, dt_object.day
        print(log)
        payload = ','.join(f'"{str(log[item])}"' for item in log)
        result = ""
        file_name = f"logs/{year}/{month}/{day}/{log['log_identifier']}.txt"
        # Upload the payload to S3
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=payload,
            ContentType='text/plain'
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'result': result, 's3_payload': payload})
        }

    except Exception as e:
        # Log any errors for debugging
        logger.error(f"Error during invocation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'sent_payload': payload  # Return the payload sent to S3 for debugging
            })
        }