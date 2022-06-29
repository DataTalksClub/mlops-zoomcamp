import os
import json
import boto3
import logging


def lambda_handler(event, context):
    # Simply put event data to kinesis data streams.
    logger = logging.getLogger()
    logger.setLevel('INFO')
    logger.info('event: {}'.format(event))

    try:
        client = boto3.client('kinesis')
        response = client.put_record(
            Data=json.dumps(event),
            PartitionKey='123',
            StreamName=os.environ.get('OUTPUT_KINESIS_STREAM')
        )
        logger.info('response: {}'.format(response))

        client = boto3.client('s3')
        response = client.put_object(
            Data=json.dumps(event),
            PartitionKey='123',
            StreamName=os.environ.get('OUTPUT_KINESIS_STREAM')
        )

        s3 = boto3.resource('s3')
        object = s3.Object(os.environ.get('BUCKET_NAME'), 'temp_file.json')  # TODO: filename?
        object.put(Body=json.dumps(event))

        logger.info('response: {}'.format(response))

    except Exception as e:
        logger.error('error: {}'.format(e))
