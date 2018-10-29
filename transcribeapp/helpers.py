import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
import hashlib
from .config import AWSConfig

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'mp4', 'flac'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


s3 = boto3.client(
    "s3",
    aws_access_key_id=AWSConfig.AWS_KEY,
    aws_secret_access_key=AWSConfig.AWS_SECRET
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWSConfig.AWS_REGION,
    aws_access_key_id=AWSConfig.AWS_KEY,
    aws_secret_access_key=AWSConfig.AWS_SECRET
)
job_table = dynamodb.Table(AWSConfig.DYNAMODB_JOBTABLE)
user_table = dynamodb.Table(AWSConfig.DYNAMODB_USERTABLE)


def upload_file_to_s3(file, bucket_name=AWSConfig.S3_BUCKET, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # may switch to log later
        print("Error: ", e)
        return e

    bucket_location = 'http://{}.s3.amazonaws.com/'.format(bucket_name)

    return "{}{}".format(bucket_location, file.filename)


def get_word_list_from_s3(s3key):
    try:
        bucket, key = s3key.split('/', 1)
        json_object = s3.get_object(Bucket=bucket, Key=key)
        jsonBody = json_object['Body'].read()
        jsonDict = json.loads(jsonBody)
        items = jsonDict['results']['items']
        if isinstance(items, str):
            return eval(items)
        else:
            return items
    except Exception as e:
        print("Error: ", e)
        return ['S3 Object not found or parse error.']
    

# dynamodb
class DecimalEncoder(json.JSONEncoder):
    # Helper class to convert a DynamoDB item to JSON.
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def scan_transcribe_table():
    pe = "JobId, CreatedAt, CompletedAt, #st, FileName, FileFormat, S3Key"
    ean = {"#st": "Status"}

    results = []
    response = job_table.scan(ProjectionExpression=pe,
                          ExpressionAttributeNames=ean)
    results.extend(response['Items'])

    while 'LastEvaluatedKey' in response:
        response = job_table.scan(ProjectionExpression=pe,
                              ExpressionAttributeNames=ean,
                              ExclusiveStartKey=response['LastEvaluatedKey'])
        results.extend(response['Items'])
    results_sorted = sorted(results, key=lambda k: k['CreatedAt'],
                            reverse=True)
    return results_sorted


def check_user(username, password):
    try:
        user = user_table.get_item(
            Key={
                'username': username
            }
        )
    except:
        return (False, "Username/Password does not match")
    else:
        user_req = user['Item']
        salty_password = (user_req['password_salt']+password).encode()
        password_hash = hashlib.sha256(salty_password).hexdigest()
        if password_hash == user_req['password_hash']:
            return (True, "Login succeeded.")
        else:
            return (False, "Username/Password does not match")
