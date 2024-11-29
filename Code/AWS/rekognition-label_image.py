import json
import boto3

def get_labels(photo, bucket):
     client = boto3.client('rekognition')
     response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10)
     return response

def lambda_handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    labels = get_labels(filename, bucket)
    
    return {
        'statusCode': 200,
        'bucket': bucket,
        'filename': filename,
        'Labels': json.dumps(labels)
    }