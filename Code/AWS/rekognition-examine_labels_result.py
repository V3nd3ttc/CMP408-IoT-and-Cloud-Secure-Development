import os

def lambda_handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    human = None
    keywords = ["human", "male", "female", "adult", "child", "people"]
    labels = event["Labels"].lower()
    
    noPrefixFilename = os.path.basename(filename)
    
    for keyword in keywords:
        if keyword in labels:
            human = True
            break
        else:
            human = False
            break
    
    return {
            'statusCode': 200,
            'bucket': bucket,
            'filename': filename,
            'noPrefixFilename': noPrefixFilename,
            "human": human
    }