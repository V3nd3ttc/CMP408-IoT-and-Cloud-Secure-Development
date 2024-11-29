import boto3
import os

def lambda_handler(event, context):
    error = event["Error"]
    cause = event["Cause"]      
    
    SENDER = os.environ['EMAIL_FROM']
    RECIPIENT = os.environ['EMAIL_TO']
    AWS_REGION = "REDACTED"
    SUBJECT = "WatchDog AWS Error"
    BODY_TEXT = ("There was an error during processing in AWS.\n")
    BODY_HTML = """<html>
    <body>
        <h1>There was an error during processing in AWS.</h1>
        <h2 style='color:red'>Error:"""+ error + """"</h2>
        <h2 style='color:red'>Cause:"""+ cause + """"</h2>
    </body>
    </html>"""            
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    #Provide the contents of the email.
    client.send_email(Destination={'ToAddresses': [RECIPIENT]},
        Message={
            'Body': {
                'Html': {'Charset': CHARSET, 'Data': BODY_HTML},
                'Text': {'Charset': CHARSET, 'Data': BODY_TEXT,},
            },
            'Subject': {'Charset': CHARSET, 'Data': SUBJECT,},
        },
        Source=SENDER,
    )
    return {
        'statusCode': 200,
    }