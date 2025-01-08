import json
import boto3
import os

UNITS_TABLE_NAME = os.getenv("UNITS_TABLE_NAME")
UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")

CLIENTS_TABLE_NAME = os.getenv("CLIENTS_TABLE_NAME")
CLIENTS_TABLE_ARN = os.getenv("CLIENTS_TABLE_ARN")

dynamodb = boto3.client('dynamodb')


def format(unit: dict, client=None) -> dict:
    # print(unit,client)
    formatted_item = {}
    formatted_item["unit_id"] = unit["id"]['S']
    formatted_item["size"] = unit["size"]['S']
    formatted_item["location"] = unit["location"]['S']
    formatted_item["monthly_price"] = unit["information"]['M']["details"]['M']["price"]['N']
    state = unit["information"]["M"]["unit_state"]["S"]
    formatted_item["renter"] = unit["information"]['M']["details"]['M']["renter"]["S"]
    formatted_item["open"] = unit["information"]['M']["details"]['M']["is_open"]["BOOL"]
    formatted_item["state"] = state

    if unit["information"]['M']["details"]['M']["shared"]["BOOL"]:
        shared_list = []
        for email in unit["information"]['M']["details"]['M']["shared_with"]["L"]:
            shared_list.append(email["S"])
        formatted_item["shared"] = {
            "shared_with": shared_list
        }

    for item in client:
        my_units = client['units']['L']
        
        # Loop through each unit in the 'units' list
        for client_unit in my_units:
            if client_unit['M']['unit_id']['S'] == unit["id"]['S']:
                billing_option_found = client_unit['M']['unit_billing_option']['S']
                accrued_cost_found = client_unit['M']['accrued_cost']['N']
                end_date_found = client_unit['M']['end_date']['S']
                unit_payment_type_found = client_unit['M']['unit_payment_type']['S']
                unit_payment_type_found = client_unit['M']['unit_payment_type']['S']
                formatted_item['billing_option'] = billing_option_found
                formatted_item['accrued_cost'] = accrued_cost_found
                formatted_item['end_date'] = end_date_found
                formatted_item['unit_payment_type'] = unit_payment_type_found
                break

        if billing_option_found:
            break 
    return formatted_item


def lambda_handler(event, context):
    # default response
    response_body = {'Message': 'get_units crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # request_body = json.loads(event['body'])
        request_body = event
        print(str(request_body))
        if "unit_id" not in request_body:
            print("unit_id not in request body")
            raise Exception("Invalid paramaters. Expected 'unit_id'")
        else:
            unit_id = request_body['unit_id']

        print("scanning dynamo")
        unit_response = dynamodb.query(
            TableName=UNITS_TABLE_ARN,
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={':id': {'S': unit_id}}
        )
        unit = unit_response['Items'][0]
        print(f"Found from scan: {str(unit_response)}")

        state = unit["information"]['M']['unit_state']['S']
        print("State: " + str(state))

        print("scanning clients")
        client_id = unit["information"]['M']["details"]['M']["renter"]["S"]
        print(client_id)
        client_response = dynamodb.query(
            TableName=CLIENTS_TABLE_ARN,
            KeyConditionExpression='id = :client_id',
            ExpressionAttributeValues={':client_id': {'S': client_id}}
        )
        client = client_response['Items'][0]
        # print(f"client Response: {str(client_response)}")


        # print(f"Dynamo Response: {str(dynamo_response)}")

        print("formatting item")
        formatted_item = format(unit, client)

        status_code = 200
        response_body = formatted_item
        print(f"sending response to client {str(response_body)}")

    except Exception as err:
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
