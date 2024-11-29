import json
import boto3
import time

def lambda_handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    noPrefixFilename = event['noPrefixFilename']
    human = event['human']
    
    
    ssm_client = boto3.client('ssm')
    instance_id = "REDACTED"
    document_name = "AWS-RunShellScript"
    
    noExtenstionFilename = noPrefixFilename.split('.')[0]
    
    # Define parameter values
    parameters = {
        "commands": [f"runuser -l martin -c 'python3 /home/martin/WatchDog/scripts/uploadAWS.py {noExtenstionFilename} -V'"]
    }
    
    response_ssm = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName=document_name,
        Parameters=parameters
    )
    
    command_id = response_ssm['Command']['CommandId']
    time.sleep(1)
    ssm_commandresult = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
    ssm_status = ssm_commandresult['Status']

    while ssm_status != 'Success':
        time.sleep(5)
        ssm_commandresult = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        ssm_status = ssm_commandresult['Status']
    return {
            'statusCode': 200,
            'bucket': bucket,
            'filename': filename,
            'noPrefixFilename': noPrefixFilename,
            'noExtenstionFilename': noExtenstionFilename,
            "human": human
    }