import os
from confluent_kafka import Consumer, KafkaException
import boto3

# Get environment variables for AWS Lambda and Kafka configuration
lambda_function_name = os.getenv('LAMBDA_FUNCTION_NAME', "bsc-2024-gameday-tigers")
kafka_topic = os.getenv('KAFKA_TOPIC', 'gameday')
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS','kafka.kafka.svc.cluster.local:9092')
group_id = os.getenv('KAFKA_GROUP_ID', 'bsc-2024-gameday-tigers')
auto_offset_reset = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
aws_region = os.getenv('AWS_REGION', 'us-east-1')
# AWS Lambda Client
lambda_client = boto3.client('lambda', region_name=aws_region)

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': auto_offset_reset
}

consumer = Consumer(consumer_config)
consumer.subscribe([kafka_topic])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        # Process Kafka message
        payload = msg.value().decode('utf-8')

        # Invoke AWS Lambda function
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='Event',  # Async invocation
            Payload=payload.encode('utf-8')
        )
        offset = msg.offset()
        print(f'Lambda invoked: {response} {offset}')

except KeyboardInterrupt:
    pass
finally:
    # Close down the consumer
    consumer.close()

