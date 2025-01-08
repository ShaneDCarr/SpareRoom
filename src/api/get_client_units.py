import json
import boto3
import os

CLIENTS_TABLE_NAME = os.getenv("CLIENTS_TABLE_NAME")
CLIENTS_TABLE_ARN = os.getenv("CLIENTS_TABLE_ARN")
UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")

dynamodb = boto3.client('dynamodb')


def read_id(unit_id):
    location = ""
    size = ""
    unit_points = unit_id.split("_")
    abrev = unit_points[2]
    siz = unit_points[1]

    if abrev == "EC0":
        location = "Eastern Cape"
    elif abrev == "FS0":
        location = "Free State"
    elif abrev == "GP0":
        location = "Gauteng"
    elif abrev == "KZN":
        location = "KwaZulu-Natal"
    elif abrev == "LP0":
        location = "Limpopo"
    elif abrev == "MP0":
        location = "Mpumalanga"
    elif abrev == "NC0":
        location = "Northern Cape"
    elif abrev == "NW0":
        location = "North-West"
    elif abrev == "WC0":
        location = "Western Cape"

    if siz == "LOC":
        size = "Locker"
    elif siz == "SML":
        size = "Small"
    elif siz == "MED":
        size = "Medium"
    elif siz == "LRG":
        size = "Large"
    print("read id")
    return location, size


def format(unit: dict) -> dict:
    formatted_item = {}
    print("units in item")
    print(str(unit))
    formatted_item["unit_id"] = unit['M']['unit_id']['S']
    location, size = read_id(formatted_item['unit_id'])
    formatted_item["location"] = location
    formatted_item["size"] = size
    formatted_item["end_date"] = unit['M']['end_date']['S']
    shared = unit['M']['shared']['BOOL']
    formatted_item["shared"] = shared
    formatted_item["accrued_cost"] = unit['M']["accrued_cost"]["N"]
    if shared:
        shared_items = unit['M']['shared_with']['L']
        shared_with = []
        for item in shared_items:
            shared_with.append(item['S'])
        formatted_item["shared_with"] = shared_with
    print(formatted_item)
    return formatted_item


def get_shared_units(client_id):
    shared_units = dynamodb.scan(
        TableName=UNITS_TABLE_ARN,
        FilterExpression="information.details.#is_shared = :new_value",
        ExpressionAttributeNames={
            "#is_shared": "shared"
        },
        ExpressionAttributeValues={
            ':new_value': {
                'BOOL': True
            }
        }
    )

    print(f"All shared_units: {str(shared_units)}")

    users_shared_with_client = []
    for unit in shared_units["Items"]:
        shared_list = unit["information"]["M"]["details"]["M"]["shared_with"]["L"]
        for person in shared_list:
            if client_id == person["S"]:
                users_shared_with_client.append(
                    (
                        unit["information"]["M"]["details"]["M"]["renter"]["S"],
                        unit["id"]["S"]
                    )
                )

    print(f"Users sharing with client: {str(users_shared_with_client)}")

    units_shared_with_client = []
    for user, unit_id in users_shared_with_client:
        dynamo_response = dynamodb.query(
            TableName=CLIENTS_TABLE_NAME,
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={':id': {'S': user}}
        )

        for unit in dynamo_response["Items"][0]["units"]["L"]:
            if unit["M"]["unit_id"]["S"] == unit_id:
                units_shared_with_client.append(unit)

    return units_shared_with_client


def lambda_handler(event, context):
    # Default response
    response_body = {'Message': 'get_client_units crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    print(f"Context: {str(context)}")

    try:
        request_body = event
        print(str(request_body))
        client = request_body.get('client')
        if not client:
            print("email not in request_body")
            raise ValueError("Missing 'client' in request body")

        print("Scanning dynamo")
        # Scan the DynamoDB table to retrieve items based on email
        dynamo_response = dynamodb.query(
            TableName=CLIENTS_TABLE_NAME,
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={':id': {'S': client}}
        )
        print(str(dynamo_response))
        # client_units = [] if not dynamo_response["Items"] else dynamo_response['Items'][0]["units"]["L"]
        if "units" in dynamo_response['Items'][0].keys():
            client_units = dynamo_response['Items'][0]["units"]["L"]
        else:
            client_units = []

        print("Getting shared units")
        shared_with_client = get_shared_units(client)
        [client_units.append(shared_unit) for shared_unit in shared_with_client]

        print("creating item list")
        print(f"all units: {client_units}")
        item_list = []
        for item in client_units:
            formatted = format(item)
            if formatted:
                item_list.append(formatted)

        print(str(item_list))

        status_code = 200
        response_body = {
            'Message': f"Number of units found: {len(item_list)}",
            'id': client,
            'units': item_list
        }
        print(f"sending response to client: {str(response_body)}")

    except Exception as err:
        response_body['Message'] = str(err)

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
