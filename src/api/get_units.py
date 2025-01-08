import json
import boto3
import os

UNITS_TABLE_NAME = os.getenv("UNITS_TABLE_NAME")
UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")

dynamodb = boto3.client('dynamodb')


def format(item: dict, state: str, filters: dict) -> dict:
    formatted_item = {}
    if filters:
        print(f"fiters: {str(filters)}")
        if "location" in filters:
            print(f"validating location: {filters['location']} in {str(item)}")
            if item["location"]['S'].lower() == filters['location'].lower():
                pass
            else:
                return None
            print("location filter not triggered")

        if "size" in filters:
            print(f"validating size: {filters['size']} in {str(item)}")
            if item["size"]["S"].lower() == filters["size"].lower():
                pass
            else:
                return None
            print("size filter not triggered")

    if state == "available":
        formatted_item["unit_id"] = item["id"]['S']
        formatted_item["size"] = item["size"]['S']
        formatted_item["location"] = item["location"]['S']
        formatted_item["price"] = item["information"]['M']["details"]['M']["price"]['N']
        formatted_item["state"] = item["information"]["M"]["unit_state"]["S"]
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
        if "state" not in request_body:
            print("state not in request body")
            raise Exception("Invalid paramaters. Expected 'state'")
        else:
            state = request_body['state']

        # if state != "available":
        #     print("state is not available")
        #     response_body['Message'] = "Clients can only query for available units."
        #     raise Exception(
        #         "Unauthorized, clients can only request for available units"
        #     )


        print("scanning dynamo")
        item_list = []
        dynamo_response = dynamodb.scan(
            TableName=UNITS_TABLE_NAME,
            FilterExpression=f"information.#unit_state = :{state}",
            ExpressionAttributeNames={
                "#unit_state": 'unit_state'
            },
            ExpressionAttributeValues={
                f":{state}": {'S': f"{state}"}
            }
        )

        filters = {}
        if 'location' in request_body:
            filters['location'] = request_body['location']

        if 'size' in request_body:
            filters['size'] = request_body['size']


        print("creating item list")
        for i in dynamo_response['Items']:
            formatted_item = format(i, state, filters)
            if formatted_item:
                item_list.append(formatted_item)


        print(f"Item list: {str(item_list)}")
        status_code = 200
        response_body = {
            'Message': f"Number of items: {len(item_list)}",
            'state': state,
            'units': item_list
        }
        print(f"sending response to client {str(response_body)}")

    except Exception as err:
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
