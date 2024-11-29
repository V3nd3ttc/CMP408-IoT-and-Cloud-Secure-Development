import json
import boto3

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']

    sf = boto3.client('stepfunctions', region_name = 'us-east-1')
    input_dict = {'bucket': bucket, 'filename': filename}
    sf.start_execution(stateMachineArn = 'REDACTED', input = json.dumps(input_dict))
    
    return {
        'statusCode': 200,
        'Info': "Step Function Started"
    }