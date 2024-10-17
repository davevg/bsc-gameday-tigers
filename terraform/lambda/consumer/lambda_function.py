import json
import boto3
import logging
import os
import datetime
import pandas as pd
import features_eng
import io


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
MODEL_METADATA_FILE = os.getenv('MODEL_METADATA_FILE', '')
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT', '')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL', '')

# Initialize S3 client
s3_client = boto3.client('s3')
sagemaker_runtime = boto3.client('sagemaker-runtime')
sqs_client = boto3.client('sqs')

low_threshold = 0.05

threshold, mean_score, std_score = features_eng.load_model_metadata_from_s3(S3_BUCKET_NAME, MODEL_METADATA_FILE, '/tmp/test.json')

def publish_to_sqs(log_message):
    # Send message to SQS queue
    response = sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(log_message)
    )
    return response

def score_log(endpoint, payload):
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint,  
        ContentType='text/csv',
        Body=payload
    )
    sagemaker_result = json.loads(response['Body'].read().decode())
    logger.info(f"Parsed SageMaker result: {sagemaker_result}")
    sagemaker_score = sagemaker_result["scores"][0]['score']
    return sagemaker_score


def lambda_handler(event, context):
    try:
        # The payload is passed as a single log entry
        log = event['log_message']  # Extract the log message from event
        dt_object = datetime.datetime.fromtimestamp(log['timestamp'])
        year, month, day = dt_object.year, dt_object.month, dt_object.day
        payload = ','.join(f'"{str(log[item])}"' for item in log)
        header = ','.join(f'"{item}"' for item in log)
        rncols = ['log_identifier', 'timestamp', 'log_level', 'ip_address', 'user_id', 'method', 'path', 'status_code', 'response_time']
        full_df = pd.read_csv(io.StringIO(header + '\n' + payload + '\n'), delimiter=",")
        df = full_df.iloc[:1].copy()  
        features_eng.df_cleaning(df, columns=rncols, inplace=True)
        prepared_data, prepared_df = features_eng.create_prepared_numpy_array(df)        
        prepared_data_csv = '\n'.join([','.join(map(str, row)) for row in prepared_data]) 
        prepared_data_csv = prepared_data_csv.encode('utf-8')  # Encode as bytes
        sagemaker_score = score_log(SAGEMAKER_ENDPOINT, prepared_data_csv)
        outlier = 1 if sagemaker_score > threshold else 0
        result = "High Outlier" if outlier else "Normal"
        logger.info(f"Result: {result} ({sagemaker_score}) {threshold} {log}")
        # Send the log message to SQS
        response = publish_to_sqs(payload + ',"' + str(sagemaker_score) + '","' + str(outlier) + '"')
        log.update({'sagemaker_score': sagemaker_score, 'outlier': outlier, 'result': result, 'threshold': threshold})
        return {
            'statusCode': 200,
            'body': json.dumps(log)
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