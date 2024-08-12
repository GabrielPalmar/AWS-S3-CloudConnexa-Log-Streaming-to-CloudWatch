import boto3
import gzip
import json
import io
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
cw_client = boto3.client('logs')

LOG_GROUP_NAME = 'CloudConnexa-S3-Logs'
LOG_STREAM_NAME = 'Lambda-Stream'

def lambda_handler(event, context):
    try:
        # Log the start of the Lambda function execution
        logger.info("Lambda function invoked")

        # Extract S3 bucket and object key from the event
        s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_file_name = event["Records"][0]["s3"]["object"]["key"]
        
        logger.info(f"Processing file {s3_file_name} from bucket {s3_bucket_name}")
        
        # Get the object from S3
        s3_object = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_file_name)
        gzipped_content = s3_object['Body'].read()
        
        # Read and decode gzip file content
        with gzip.GzipFile(fileobj=io.BytesIO(gzipped_content)) as f:
            file_content = f.read().decode('utf-8')
        
        log_entry = json.loads(file_content)
        timestamp_str = log_entry['timestamp']
        
        # Convert timestamp to Unix time in milliseconds
        timestamp = int(datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() * 1000)
        
        # logger.info(f"Log entry: {json.dumps(log_entry, indent=2)}")

        # Ensure log group exists
        try:
            cw_client.create_log_group(logGroupName=LOG_GROUP_NAME)
        except cw_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Log group {LOG_GROUP_NAME} already exists")
        
        # Ensure log stream exists
        try:
            cw_client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
        except cw_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Log stream {LOG_STREAM_NAME} already exists")
        
        # Get the sequence token
        response = cw_client.describe_log_streams(
            logGroupName=LOG_GROUP_NAME,
            logStreamNamePrefix=LOG_STREAM_NAME
        )
        
        log_streams = response['logStreams']
        if len(log_streams) == 1:
            sequence_token = log_streams[0].get('uploadSequenceToken', None)
            logger.info(f"Sequence token: {sequence_token}")
        else:
            sequence_token = None
            logger.info("No sequence token found")
        
        # Prepare log events
        log_events = [
            {
                'timestamp': timestamp,
                'message': json.dumps(log_entry)
            }
        ]
        
        # Put log events to CloudWatch
        put_log_events_args = {
            'logGroupName': LOG_GROUP_NAME,
            'logStreamName': LOG_STREAM_NAME,
            'logEvents': log_events
        }
        
        if sequence_token:
            put_log_events_args['sequenceToken'] = sequence_token
        
        put_log_events_response = cw_client.put_log_events(**put_log_events_args)
        logger.info(f"Put log events response: {put_log_events_response}")
        
        return {
            'statusCode': 200,
            'body': 'Successfully processed and sent log entries to CloudWatch'
        }

    except Exception as e:
        logger.error(f"Error processing log event: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': f'Error processing log event: {str(e)}'
        }