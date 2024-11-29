import json
import boto3

def lambda_handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    noPrefixFilename = event['noPrefixFilename']
    human = event['human']

    s3 = boto3.client('s3')
    
    if human:
        destination = f"processed/positive/{noPrefixFilename}"
    else:
        destination = f"processed/false-positive/{noPrefixFilename}"
    
    # Copy object
    source = {'Bucket': bucket, 'Key': filename}
    s3.copy(source, bucket, destination)
    
    # Delete original object
    s3.delete_object(Bucket=bucket, Key=filename)

    return {
        'statusCode': 200,
        'body': json.dumps(f'File {filename} in {bucket} moved succesfully to {destination} in {bucket}')
    }