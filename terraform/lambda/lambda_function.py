import json
import boto3
import logging
import os
import datetime
import time
import random # Temp so we can generate front end..
from decimal import Decimal
import pandas as pd
import features_eng
import io


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT', '')

# Initialize S3 client
s3_client = boto3.client('s3')
sagemaker_runtime = boto3.client('sagemaker-runtime')

# These will change with the 3 sigma score..
high_threshold = 0.95
low_threshold = 0.05


def score_log(endpoint, payload):
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint,  
        ContentType='text/csv',
        Body=payload
    )
    sagemaker_result = json.loads(response['Body'].read().decode())
    logger.info(f"Parsed SageMaker result: {sagemaker_result}")
    sagemaker_score = [datum["score"] for datum in results["scores"]]
    return sagemaker_score


def lambda_handler(event, context):
    
    # -------------- NSTART ---------------------
    print(" =++++++++++++++ ****************** +++++++++++++++")        
    print(" =++++++++++++++ ****************** +++++++++++++++")        
    
    downloaded_data_bucket = "bsc-2024-gameday-tigers" 
    downloaded_data_prefix = "dataset"
    data_filename = "small.csv"
    file_key = f"{downloaded_data_prefix}/{data_filename}"
    
    # Download the file to the /tmp directory
    local_file_path = f"/tmp/{data_filename}"
    
    print(f"file path = {downloaded_data_bucket}/{file_key}")
    
    # Load data
    s3_client.download_file(downloaded_data_bucket, file_key, local_file_path)
    df = pd.read_csv(local_file_path, delimiter=",")
    
    print(f"df size = {df.shape}")
    print(" =++++++++++++++ ****************** +++++++++++++++")   
    # Clearn the data 
    rncols = ['log_identifier', 'timestamp', 'log_level', 'ip_address', 'user_id', 'method', 'path', 'status_code', 'response_time']
    features_eng.df_cleaning(df, columns=rncols, inplace=True)

    # prepare input for training/infernece
    prepared_data, prepared_df = features_eng.create_prepared_numpy_array(df)
    print(f"prepared_df = {prepared_df.head(2)}")
    
    # convert numpy data to csv string 
    prepared_data_csv = '\n'.join([','.join(map(str, row)) for row in prepared_data])  # Convert NumPy array to CSV format
    prepared_data_csv = prepared_data_csv.encode('utf-8')  # Encode as bytes


    print(" =++++++++++++++ ****************** +++++++++++++++")  
    # Call the endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='text/csv',
        Body=prepared_data_csv
    )
    results = json.loads(response['Body'].read().decode())
    scores = [datum["score"] for datum in results["scores"]]
    print(f"Score size = {len(scores)}")
    
    # Update original df with score 
    df = features_eng.append_score_and_outlier_to_df(df, scores)
    print(f"New columns = {df.columns}")
    print(" =++++++++++++++ ****************** +++++++++++++++")  
    # -------------- NEND ---------------------
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

    # try:
    #     # The payload is passed as a single log entry
    #     log = event['log_message']  # Extract the log message from event
    #     dt_object = datetime.datetime.fromtimestamp(log['timestamp'])
    #     year, month, day = dt_object.year, dt_object.month, dt_object.day
    #     payload = ','.join(f'"{str(log[item])}"' for item in log)
    #     file_name = f"logs/{year}/{month}/{day}/{log['log_identifier']}.txt"
    #     # Upload the payload to S3
    #     response = s3_client.put_object(
    #         Bucket=S3_BUCKET_NAME,
    #         Key=file_name,
    #         Body=payload,
    #         ContentType='text/plain'
    #     )
    #     logger.info(f"Panda Read: {payload}")
    #     rncols = ['log_identifier', 'timestamp', 'log_level', 'ip_address', 'user_id', 'method', 'path', 'status_code', 'response_time']

    #     temp_filename = f"/tmp/tempfile_{int(time.time())}.txt"
    #     with open(temp_filename, 'w') as file:
    #         file.write(payload)
    #     df = pd.read_csv(temp_filename, delimiter=",", names=rncols)
        
                
        
    #     logger.info(f"Read Done {df}")
    #     logger.info(f"start cleaning")
    #     features_eng.df_cleaning(df, columns=rncols, inplace=True)

    #     # prepare input for training/infernece
    #     prepared_data, prepared_df = features_eng.create_prepared_numpy_array(df)

    #     sagemaker_score = score_log(SAGEMAKER_ENDPOINT, prepared_data)
    #     databricks_score = .5
    #     #databricks_score = score_log(BASELINE_SAGEMAKER_ENDPOINT ,payload)

    #     if sagemaker_score > high_threshold or databricks_score > high_threshold:
    #         result = "High Outlier"
    #     elif sagemaker_score < low_threshold or databricks_score < low_threshold:
    #         result = "Low Outlier"
    #     else:
    #         result = "Normal"
    #     logger.info(f"Result: {result}({sagemaker_score},{databricks_score}) {log}")
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps({'result': result, 's3_payload': payload, 'sagemaker_score': sagemaker_score, 'databricks_score': databricks_score})
    #     }

    # except Exception as e:
    #     # Log any errors for debugging
    #     logger.error(f"Error during invocation: {str(e)}")
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps({
    #             'error': str(e),
    #             'sent_payload': payload  # Return the payload sent to S3 for debugging
    #         })
    #     }