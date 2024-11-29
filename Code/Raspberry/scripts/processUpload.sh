#!/bin/bash

file_name="$1"

echo starting s3-upload.sh
echo uploading file $1

python3 /home/martin/WatchDog/scripts/uploadAWS.py $file_name

echo completed s3-upload.sh