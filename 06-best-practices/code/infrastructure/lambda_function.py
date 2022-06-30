import os
import json
import boto3
import logging


def lambda_handler(event, context):
    # Simply put event data to kinesis data streams.
    logger = logging.getLogger()
    logger.setLevel('INFO')
    logger.info('event: {}'.format(event))

    consumer_stream = os.environ.get('OUTPUT_KINESIS_STREAM')
    bucket = os.environ.get('BUCKET_NAME')

    try:
        client = boto3.client('kinesis')
        response = client.put_record(
            Data=json.dumps(event),
            PartitionKey='123',
            StreamName=consumer_stream
        )
        logger.info(f'response: {response} saved to consumer_stream: {consumer_stream}')

        s3 = boto3.resource('s3')
        s3.Bucket(bucket).put_object(Key='temp_file.json', Body=json.dumps(event))  # TODO: filename?
        logger.info(f'response: saved to s3: {bucket}')

    except Exception as e:
        logger.error('error: {}'.format(e))
