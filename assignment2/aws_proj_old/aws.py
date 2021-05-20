import boto3
from app_model import User
from urllib import request
import os
from boto3.dynamodb.conditions import Key

project_dir = os.path.dirname(os.path.abspath(__file__))
AWS_REGION = "us-east-2"
AWS_ACCESS_KEY = "AKIATQFHCTPYX2SYCJR5"
AWS_ACCESS_SECRET = "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"
dynamodb = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_ACCESS_SECRET, region_name=AWS_REGION)
dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                                   aws_secret_access_key=AWS_ACCESS_SECRET, region_name=AWS_REGION)
s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_ACCESS_SECRET)
s3Client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_ACCESS_SECRET)
BUCKET = "flask-aws-project"


def get_user_with_email(email):
    table = dynamodb_resource.Table("User")
    user = table.get_item(
        Key={'email': email}
    )
    if "Item" in user:
        item = user["Item"]
        user = User()
        user.email = item["email"]
        user.password = item["password"]
        user.username = item["username"]
        return user
    else:
        return None


def get_music_by_title(title):
    table = dynamodb_resource.Table("Music")
    music = table.get_item(
        Key={"title": title}
    )
    if "Item" in music:
        return music["Item"]
    else:
        return {}


def get_music_list():
    table = dynamodb_resource.Table("Music")
    music = table.scan()
    if "Items" in music:
        return music["Items"]
    else:
        return []


def put_user_to_db(email=None, username=None, password=None, item_dict=None):
    table = dynamodb_resource.Table('User')
    item = item_dict if item_dict else {
        'email': email,
        'password': password,
        'username': username
    }
    response = table.put_item(Item=item)


def put_music(item):
    table = dynamodb_resource.Table("Music")
    table.put_item(Item=item)


def put_subscription(item):
    table = dynamodb_resource.Table("user_subscription")
    table.put_item(Item=item)


def get_user_subscriptions(user_email: str):
    table = dynamodb_resource.Table("user_subscription")
    subscriptions = table.scan()
    if "Items" in subscriptions:
        subscriptions = subscriptions["Items"]
        subscriptions = [subscription for subscription in subscriptions if
                         subscription["user"].lower() == user_email.lower()]
        return subscriptions
    else:
        return []


def delete_subscription(id):
    table = dynamodb_resource.Table("user_subscription")
    try:
        table.delete_item(
            Key={"id": id}
        )
        return True
    except:
        return False


# print(get_user_with_email("test1@yopmail.com"))

def upload_to_s3(url):
    try:
        key = url.split('/')[::-1][0]  # In my situation, ids at the end are unique
        file_path = "{}/images/{}".format(project_dir, key)
        file_object = request.urlretrieve(url, file_path)  # 'Like' a file object
        print(file_object, key)
        s3Client.put_object(Body=open(file_path, 'rb'), Bucket=BUCKET, Key=key)
        return "Success"
    except:
        pass
