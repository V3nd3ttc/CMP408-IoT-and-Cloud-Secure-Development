import boto3
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    noPrefixFilename = event['noPrefixFilename']
    noExtenstionFilename = event['noExtenstionFilename']
    human = event['human']
    
    jpgFileLocationS3 = filename
    mp4FileLocationS3 = f"processed/positive/{noExtenstionFilename}.mp4"
    tmpJpgLocation = f"/tmp/{noExtenstionFilename}.jpg"
    tmpMp4Location = f"/tmp/{noExtenstionFilename}.mp4"
    
    SENDER = os.environ['EMAIL_FROM']
    RECIPIENT = os.environ['EMAIL_TO']
    AWS_REGION = "REDACTED"
    
    s3 = boto3.client('s3', region_name=AWS_REGION)
    s3.download_file(bucket, jpgFileLocationS3, tmpJpgLocation)
    s3.download_file(bucket, mp4FileLocationS3, tmpMp4Location)
    
    SUBJECT = "WatchDog HUMAN detected"
    BODY_TEXT = ("WatchDog has detected a human.\n")
    BODY_HTML = """\
    <html>
    <body>
    <h1>WatchDog has detected a human.</h1>
    </body>
    </html>
    """            
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    ses = boto3.client('ses',region_name=AWS_REGION)
    
    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    
    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')
    
    # Encode the text and HTML content and set the character encoding.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    
    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    
    # Define the attachment part and encode it using MIMEApplication.
    attachmentJpg = MIMEApplication(open(tmpJpgLocation, 'rb').read())
    attachmentMp4 = MIMEApplication(open(tmpMp4Location, 'rb').read())
    
    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    attachmentJpg.add_header('Content-Disposition','attachment',filename=f"{noExtenstionFilename}.jpg")
    attachmentMp4.add_header('Content-Disposition','attachment',filename=f"{noExtenstionFilename}.mp4")
    
    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)
    
    # Add the attachment to the parent container.
    msg.attach(attachmentJpg)
    msg.attach(attachmentMp4)
    
    #Provide the contents of the email.
    ses.send_raw_email(
        Source=SENDER,
        Destinations=[RECIPIENT],
        RawMessage={'Data':msg.as_string()},
    )
        
    return {
            'statusCode': 200,
            'bucket': bucket,
            'filename': filename,
            'noPrefixFilename': noPrefixFilename,
            "human": human
    }