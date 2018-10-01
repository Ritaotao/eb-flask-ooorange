import os
import json

class Config(object):
    SECRET_KEY = os.urandom(32)
    PORT = 5000

class AWSConfig(object):
    try:
        AWS_REGION = os.environ['AWS_REGION']
        AWS_KEY = os.environ['AWS_KEY']
        AWS_SECRET = os.environ['AWS_SECRET']
        S3_BUCKET = os.environ['S3_BUCKET']
        DYNAMODB_JOBTABLE = os.environ['DYNAMODB_JOBTABLE']
        DYNAMODB_USERTABLE = os.environ['DYNAMODB_USERTABLE']
    except:
        print('Use env variables stored locally...')
        with open('env.json') as fp:
            ENV = json.load(fp)
        AWS_REGION = ENV['AWS_REGION']
        AWS_KEY = ENV['AWS_KEY']
        AWS_SECRET = ENV['AWS_SECRET']
        S3_BUCKET = ENV['S3_BUCKET']
        DYNAMODB_JOBTABLE = ENV['DYNAMODB_JOBTABLE']
        DYNAMODB_USERTABLE = ENV['DYNAMODB_USERTABLE']
