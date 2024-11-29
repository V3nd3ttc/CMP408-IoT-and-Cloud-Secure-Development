#!/usr/bin/env python3

import boto3
from datetime import date
import argparse
from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(26)

AWS_S3_BUCKET_NAME = 'REDACTED'
AWS_REGION = 'REDACTED'
AWS_ACCESS_KEY = 'REDACTED'
AWS_SECRET_KEY = 'REDACTED'

today = date.today()
date = today.strftime("%Y-%m")

parser = argparse.ArgumentParser()
parser.add_argument('filename', action='store', type=str, help="Name of file to upload")
parser.add_argument("-V", action="store_true", help="Use to upload video to AWS")
args = parser.parse_args()

prefix = ""

if args.V:
    fileName = args.filename + ".mp4"
    prefix = "processed/positive/"
else:
    fileName = args.filename + ".jpg"
    prefix = "upload/"

fileLocation = '/home/REDACTED/WatchDog/www/recordings/%s/%s' % (date, fileName)

LOCAL_FILE = fileLocation
NAME_FOR_S3 = fileName

def beep():
    buzzer.on()
    sleep(0.1)
    buzzer.off()

def main():
    beep()
    print('in main method')

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    response = s3_client.upload_file(LOCAL_FILE, AWS_S3_BUCKET_NAME, prefix + NAME_FOR_S3)

    print(f'upload_log_to_aws response: {response}')
    return 0

if __name__ == '__main__':
    main()