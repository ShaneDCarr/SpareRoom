import json
import boto3
import os


CLIENTS_TABLE_NAME = os.getenv("CLIENTS_TABLE_NAME")
CLIENTS_TABLE_ARN = os.getenv("CLIENTS_TABLE_ARN")

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


def update_payment(client: dict, unit_id: str, new_payment: str):

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

    expression = f"SET units[{unit_index}].unit_payment_type = :new_payment"

    dynamo.update_item(
        TableName=CLIENTS_TABLE_ARN,
        Key={
            'id': {'S': client['id']['S']}
        },
        UpdateExpression=expression,
        ExpressionAttributeValues={
            ":new_payment": {'S': new_payment}
        },
        ReturnValues="UPDATED_NEW"
    )
    print(f"Updated payment: {new_payment}.")


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
        new_payment = event['value']

        print(f"Email: {email}")
        print(f"Unit ID: {unit_id}")
        print(f"New payment: {new_payment}")

        # Fetch client info
        client = get_client_info(email)
        print("Client info yay")

        update_payment(client, unit_id, new_payment)

        status_code = 200
        response_body['Message'] = f"new payment is: {new_payment}"

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
