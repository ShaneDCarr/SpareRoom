import json
import boto3
import os
import pytz
from datetime import datetime


UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")
UNITS_TABLE_NAME = os.getenv("UNITS_TABLE_NAME")
NOTIFICATIONS_TABLE_NAME = os.getenv("NOTIFICATIONS_TABLE_NAME")

dynamo = boto3.client('dynamodb')
sast = pytz.timezone('Africa/Johannesburg')

def get_unit(unit_id: str):
    query = dynamo.query(
        TableName=UNITS_TABLE_ARN,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {
                'S': unit_id
            }
        }
    )
    unit = query['Items'][0]
    return unit


def switch_openness(unit: dict):
    return not unit['information']['M']['details']['M']['is_open']['BOOL']


def update_unit(unit: dict, openness: bool):
    return dynamo.update_item(
        TableName=UNITS_TABLE_ARN,
        Key={
            'id': {'S': unit['id']['S']}
        },
        UpdateExpression="SET information.details.is_open = :new_value",
        ExpressionAttributeValues={
            ":new_value": {'BOOL': openness}
        },
        ReturnValues="UPDATED_NEW"

    )

def log_notification(unit_id:str, client_email:str, action:str):
    """
    Log action performed on a unit
    """
    try:
        print(NOTIFICATIONS_TABLE_NAME)
        timestamp = datetime.now(sast).strftime('%Y-%m-%d %H:%M:%S')
        new_notification = {
            "time": timestamp,
            "user": client_email,
            "action": action
        }

        dynamo.update_item(
            TableName=NOTIFICATIONS_TABLE_NAME,
            Key={'unit_id': {'S': unit_id}},
            UpdateExpression="SET notifications = list_append(if_not_exists(notifications, :empty_list), :new_notification)",
            ExpressionAttributeValues={
                ":new_notification": {"L": [{'M': {
                    'time': {'S': new_notification['time']},
                    'user': {'S': new_notification['user']},
                    'action': {'S': new_notification['action']}
                }}]},
                ":empty_list": {'L': []}
            }
        )
        print(f"Notification logged for unit {unit_id} by {client_email}: ${action}")
    except Exception as e:
        print(f"Error logging notifications: {e}")



def lambda_handler(event, context):
    # default response
    response_body = {'Message': 'open_unit crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    try:
        client = event['client']
        unit_id = event['unit_id']
        print(f"Getting unit {unit_id}")

        unit = get_unit(unit_id)
        print(f"Got unit: {str(unit)}")

        openless = switch_openness(unit)
        print(f"Open negation: {openless}")

        print(f"Updating unit to open = {openless}")
        response = update_unit(unit, openless)
        print(f"Response from dynamo for {unit_id}: {response}")

        if openless == True:
            adverb = "Opened"
        else:
            adverb = "Closed"
        log_notification(unit_id, client, adverb)

        status_code = 200
        response_body['Message'] = f"{adverb} unit."


    except IndexError as index_error:
        response_body['Message'] = "Item not found"
    except KeyError as e:
        response_body["Message"] = f'Missing field: {e}'
        status_code = 400
    except Exception as e:
        print(f"Unhandled exception: {e}")
        response_body['Message'] = "An error occurred"

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
