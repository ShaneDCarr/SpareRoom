import json
import os
import boto3


CLIENTS_TABLE = os.getenv("CLIENT_TABLE_ARN")
UNITS_TABLE = os.getenv("UNITS_TABLE_ARN")

dynamo = boto3.client("dynamodb")


def get_unit_cost(unit_id: str):
    print("Getting units cost")
    unit_response = dynamo.query(
        TableName=UNITS_TABLE,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={':id': {'S': unit_id}}
    )
    print(f"Unit: {str(unit_response)}")
    cost = unit_response['Items'][0]['information']['M']['details']['M']['price']['N']
    print(f"Got unit costs R{cost}")
    return cost

def write_to_unit_table(unit_table_info: dict):
    details_update = dynamo.update_item(
        TableName=UNITS_TABLE,
        Key={
            'id': {'S': unit_table_info['unit_id']}
        },
        UpdateExpression="SET information.details = :new_value",
        ExpressionAttributeValues={
            ":new_value": {
                'M': {
                    "end_date": {"S": unit_table_info["end_date"]},
                    "is_open": {"BOOL": unit_table_info["is_open"]},
                    "renter": {"S": unit_table_info["renter"]},
                    "shared": {"BOOL": unit_table_info["shared"]},
                    "price": {"N": unit_table_info["price"]}
                }
            }
        },
        ReturnValues="UPDATED_NEW"
    )

    state_update = dynamo.update_item(
        TableName=UNITS_TABLE,
        Key={
            'id': {'S': unit_table_info['unit_id']}
        },
        UpdateExpression="SET information.unit_state = :new_value",
        ExpressionAttributeValues={
            ":new_value": {'S': "Reserved"}
        },
        ReturnValues="UPDATED_NEW"
    )

    return [details_update, state_update]


def write_to_client_table(client_table_info: dict):
    return dynamo.update_item(
        TableName=CLIENTS_TABLE,
        Key={
            'id': {'S': client_table_info['client']}
        },
        UpdateExpression="SET units = list_append(if_not_exists(units, :empty_list), :new_value)",
        ExpressionAttributeValues={
            ":new_value": {
                'L': [{
                    "M": {
                            "end_date": {"S": client_table_info["end_date"]},
                            "shared": {"BOOL": client_table_info["shared"]},
                            "price": {"N": client_table_info["accrued_cost"]},
                            "accrued_cost": {"N": client_table_info["accrued_cost"]},
                            "unit_payment_type": {"S": client_table_info["payment_type"]},
                            "unit_billing_option": {"S": client_table_info["billing_option"]},
                            "unit_id": {"S": client_table_info["unit_id"]}
                    }
                }]
            },
            ':empty_list': {'L': []}
        },
        ReturnValues="UPDATED_NEW"
    )


def lambda_handler(event, context):
    response_body = {'Message': 'rent crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        print(f"Event: {str(event)}")
        request_body = json.loads(event['body'])

        if not request_body:
            raise Exception("Body invalid.")
        print(f"Request body: {str(request_body)}")

        if 'unit_id' not in request_body:
            raise Exception("'unit_id' not found")
        else:
            unit_id = request_body['unit_id']
            print(f"unit_id: {unit_id}")

        if 'end_date' not in request_body:
            raise Exception("'end_date' not found")
        else:
            end_date = request_body['end_date']
            print(f"end_date: {end_date}")

        if 'email' not in request_body:
            raise Exception("'email' not found")
        else:
            email = request_body['email']
            print(f"email: {email}")

        if 'billing_option' not in request_body:
            raise Exception("'billing_option' not found")
        else:
            billing_option = request_body['billing_option']
            print(f"billing_option: {billing_option}")

        if 'payment_type' not in request_body:
            raise Exception("'payment_type' not found")
        else:
            payment_type = request_body['payment_type']
            print(f"payment_type: {payment_type}")

        cost = get_unit_cost(unit_id)

        unit_table_info = {
            'unit_id': unit_id,
            'end_date': end_date,
            'is_open': False,
            'renter': email,
            'shared': False,
            'price': cost
        }
        print(f"UnitTableUpdateInfo: {str(unit_table_info)}")

        client_table_info = {
            'accrued_cost': cost,
            'end_date': end_date,
            'shared': False,
            'billing_option': billing_option,
            'unit_id': unit_id,
            'payment_type': payment_type,
            'client': email
        }
        print(f"ClientTableUpdateInfo: {str(client_table_info)}")

        print(f"Unit table response: {write_to_unit_table(unit_table_info)}")
        print(f"Client table response: {write_to_client_table(client_table_info)}")

        status_code = 200
        response_body["Message"] = "Unit rented successfully!"
    except Exception as err:
        response_body["Message"] = str(err)

    return {
        "statusCode": status_code,
        "body": json.dumps(response_body),
        "headers": headers
    }
