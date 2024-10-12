# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install the necessary dependencies
RUN pip install --no-cache-dir confluent_kafka boto3

# Copy the consumer code to the container
COPY kafka_consumer.py /app/kafka_consumer.py

# Command to run the consumer script
CMD ["python", "kafka_consumer.py"]

