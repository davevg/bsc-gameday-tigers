import json
import boto3
import logging
import os
import datetime
import random # Temp so we can generate front end..
from decimal import Decimal


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
bucket_name = os.getenv('S3_BUCKET_NAME', 'bsc-2024-gameday-tigers')
table_name = os.getenv('DYNAMO_TABLE_NAME', 'bsc-2024-gameday-tigers') 
# Initialize S3 client
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
high_threshold = 0.95
low_threshold = 0.05

def generate_score(log):
    # However we score should go here
    return round(random.uniform(0.00, 1.0), 2)
    #return 0.0
# Function to store log with RCF score in DynamoDB
def save_to_dynamo(log, sagemaker_score, databricks_score):
    try:
        # Get the DynamoDB table
        table = dynamodb.Table(table_name)

        # Prepare the log entry with the RCF score (convert floats to Decimal)
        log_entry = {
            'log_identifier': log['log_identifier'],
            'timestamp': Decimal(str(log['timestamp'])),
            'log_level': log['log_level'],
            'ip_address': log['ip_address'],
            'user_id': log['user_id'],
            'method': log['method'],
            'path': log['path'],
            'status_code': log['status_code'],
            'response_time': Decimal(str(log['response_time'])),
            'message': log['message'],
            'score_sagemaker': Decimal(str(sagemaker_score)), 
            'score_databricks': Decimal(str(databricks_score)),
            
        }
        log_entry['is_high_outlier'] = int(
            sagemaker_score > high_threshold or  # High outlier for SageMaker
            databricks_score > high_threshold    # High outlier for Databricks
        )
        log_entry['is_low_outlier'] = int(
            sagemaker_score < low_threshold or   # Low outlier for SageMaker
            databricks_score < low_threshold     # Low outlier for Databricks
        )
        # Log the log_entry being written to DynamoDB
        logger.info(f"Log entry being written to DynamoDB: {log_entry}")

        # Write to DynamoDB
        table.put_item(Item=log_entry)

        logger.info("Log successfully written to DynamoDB")

    except Exception as e:
        logger.error(f"Error writing to DynamoDB: {str(e)}")

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

        sagemaker_score = generate_score(payload)
        databricks_score = sagemaker_score # make them the same for now
        save_to_dynamo(log, sagemaker_score, databricks_score)

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