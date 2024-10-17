import os
from confluent_kafka import Consumer, KafkaException
import boto3
import json

# Get environment variables for AWS Lambda and Kafka configuration
lambda_function_name = os.getenv('LAMBDA_FUNCTION_NAME', "bsc-2024-gameday-tigers")
kafka_topic = os.getenv('KAFKA_TOPIC', 'gameday')
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka.kafka.svc.cluster.local:9092')
group_id = os.getenv('KAFKA_GROUP_ID', 'bsc-2024-gameday-tigers')
auto_offset_reset = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
aws_region = os.getenv('AWS_REGION', 'us-east-1')

# AWS Lambda Client
lambda_client = boto3.client('lambda', region_name=aws_region)

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': auto_offset_reset,
    'enable.auto.commit': True  # Enable automatic offset commit
}

consumer = Consumer(consumer_config)
consumer.subscribe([kafka_topic])

try:
    print("Starting Kafka consumer...")
    while True:
        # Retrieve a batch of messages (up to 100 messages)
        messages = consumer.consume(num_messages=100, timeout=1.0)

        # Process each message in the batch
        for msg in messages:
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            # Process Kafka message
            payload = msg.value().decode('utf-8')

            # Invoke AWS Lambda function
            response = lambda_client.invoke(
                FunctionName=lambda_function_name,
                InvocationType='RequestResponse',  # Async invocation
                Payload=payload.encode('utf-8')
            )
            response_payload = response['Payload'].read().decode('utf-8')
            lambda_output = json.loads(response_payload)
            print(f'{lambda_output}')


except KeyboardInterrupt:
    pass
finally:
    # Close down the consumer
    print("Shutting Down Kafka consumer...")
    consumer.close()
