import json
import boto3
import os


UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")
UNITS_TABLE_NAME = os.getenv("UNITS_TABLE_NAME")

dynamo = boto3.client('dynamodb')


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

def get_unit_state(unit: dict):
    current_state = unit['information']['M']['unit_state']['S']
    return current_state

def update_unit_state(unit: dict):
    return dynamo.update_item(
        TableName=UNITS_TABLE_ARN,
        Key={
            'id': {'S': unit['id']['S']}
        },
        UpdateExpression="SET information.unit_state = :new_value",
        ExpressionAttributeValues={
            ":new_value": {'S': "Cancelled"}
        },
        ReturnValues="UPDATED_NEW"

    )

def lambda_handler(event, context):
    # default response
    response_body = {'Message': 'cancel.py crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    try:

        unit_id = event['unit_id']
        print(f"Getting unit {unit_id}")

        new_state = event['value']
        print(f"got new state: {new_state}")

        unit = get_unit(unit_id)
        print(f"Got unit: {str(unit)}")


        current_state = get_unit_state(unit)
        print(f"current state is: {current_state}")
        print(f"Updating state to cancelled")
        if new_state.lower() == "cancelled":
            print("yes it is right")
            response = update_unit_state(unit)
            print(f"Response from dynamo for {unit_id}: {response}")
        else:
            print(f"state is not cancel, this is the state {new_state}")

        status_code = 200
        response_body['Message'] = f"{new_state} is the new state"


    except IndexError as index_error:
        response_body['Message'] = "Item not found"

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
