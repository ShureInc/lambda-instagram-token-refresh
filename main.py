import base64
import json
import os

import boto3
import requests
from botocore.exceptions import ClientError


def get_secret(secret_name, region_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        print("secret name " + secret_name)
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        print(get_secret_value_response)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.

            print("Exception DecryptionFailureException")
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.

            print("Exception InternalServiceErrorException")
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.

            print("Exception InvalidParameterException")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.

            print("Exception InvalidRequestException")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.

            print("Exception ResourceNotFoundException")
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)


def lambda_handler(event, context):
    secret_name = os.getenv('SECRETS_MANAGER_ARN')
    region_name = os.getenv('AWS_S3_REGION')
    notification = "The Instagram Token was upgraded please restart service " + os.getenv(
        'APPLICATION_NAME') + " in 48 hr"
    subject = "Instagram Token Rotation "
    try:
        snsclient = boto3.client('sns')

        ig_secret_token = get_secret(secret_name, region_name)
        print(ig_secret_token)

        print("Refreshing Token: " + ig_secret_token['IG_ACCESS_TOKEN'])

        payload = {'grant_type': 'ig_refresh_token', 'access_token': ig_secret_token['IG_ACCESS_TOKEN']}

        result = requests.get(
            'https://graph.instagram.com/refresh_access_token?access_token={}', params=payload
        )
        data = result.json()
        print("Generated Token: " + data['access_token'])
        new_access_token = data['access_token']

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        response = client.update_secret(
            SecretId=secret_name,
            SecretString='{"IG_ACCESS_TOKEN":"' + new_access_token + '"}',
        )

        print("update response: " + response)
        subject = subject + "Success"
        return response
    except Exception as e:
        print(e)
        notification = "Exception occurred for run " + context.aws_request_id
        subject = subject + "Error"
    finally:
        print("Sending Notification")

        response = snsclient.publish(
            TargetArn=os.getenv('SNS_ARN'),
            Message=json.dumps({'default': notification}),
            MessageStructure='json',
            Subject=subject
        )
        print("sns response sent")
