import json
import boto3
import os


CLIENTS_TABLE_NAME = os.getenv("CLIENTS_TABLE_NAME")
CLIENTS_TABLE_ARN = os.getenv("CLIENTS_TABLE_ARN")
UNITS_TABLE_NAME = os.getenv("UNITS_TABLE_NAME")
UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")

dynamo = boto3.client('dynamodb')


def get_client_info(email: str):

    client_response = dynamo.query(
        TableName=CLIENTS_TABLE_NAME,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={':id': {'S': email}}
    )
    print("got client info")
    if 'Items' in client_response and client_response['Items']:
        return client_response['Items'][0]
    else:
        raise IndexError("no client exists")

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


def update_stop_sharing_in_client(client: dict, unit_id: str, new_sharing_bool: bool):

    my_units = client['units']['L']
    unit_index = None

    index = 0 
    unit_index = None

    for client_unit in my_units:
        if client_unit['M']['unit_id']['S'] == unit_id:
            unit_index = index
            break
        index += 1


    if unit_index is None:
        raise ValueError(f"{unit_id} not found")

    expression = f"""
        SET units[{unit_index}].#is_shared = :new_sharing_bool
        REMOVE units[{unit_index}].shared_with
    """

    dynamo.update_item(
        TableName=CLIENTS_TABLE_ARN,
        Key={
            'id': {'S': client['id']['S']}
        },
        UpdateExpression=expression,
        ExpressionAttributeNames={
            "#is_shared": "shared"
        },
        ExpressionAttributeValues={
            ":new_sharing_bool": {'BOOL': new_sharing_bool}
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Updated shared: {new_sharing_bool} and removed shared_with")


def update_stop_sharing_unit(unit: dict, new_sharing_bool: bool):

    expression2 = """SET information.details.#is_shared = :new_sharing_bool
    REMOVE information.details.shared_with"""

    return dynamo.update_item(
        TableName=UNITS_TABLE_ARN,
        Key={
            'id': {'S': unit['id']['S']}
        },
        UpdateExpression=expression2,
        ExpressionAttributeNames={
            "#is_shared": "shared"
        },
        ExpressionAttributeValues={
            ":new_sharing_bool": {'BOOL': new_sharing_bool}
        },
        ReturnValues="UPDATED_NEW"

    )


def lambda_handler(event, context):

    response_body = {'Message': 'we crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        unit_id = event['unit_id']
        email = event['client']
        client_list = event['client']
        new_sharing_bool = False

        print(f"Email: {email}")
        print(f"Unit ID: {unit_id}")
        print(f"New sharing bool: {new_sharing_bool}")

        # Fetch client info
        client = get_client_info(email)
        print("Client info yay")

        unit = get_unit(unit_id)
        print("got unit info yay")

        update_stop_sharing_in_client(client, unit_id, new_sharing_bool)
        update_stop_sharing_unit(unit, new_sharing_bool)

        status_code = 200
        response_body['Message'] = f"{new_sharing_bool}, stopped sharing"

    except IndexError as index_error:
        response_body['Message'] = "client not found"
        print(f"Error: {index_error}")
    except ValueError as value_error:
        response_body['Message'] = str(value_error)
        print(f"Error: {value_error}")
    except Exception as e:
        response_body['Message'] = "An unexpected error occurred."
        print(f"Unexpected Error: {e}")

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }