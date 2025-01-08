import json
import boto3
import os


UNITS_TABLE_ARN = os.getenv("UNITS_TABLE_ARN")
CLIENTS_TABLE_ARN = os.getenv("CLIENTS_TABLE_ARN")

dynamo = boto3.client("dynamodb")


def update_units_table(unit_id, user):
    update_shared_bool = dynamo.update_item(
        TableName=UNITS_TABLE_ARN,
        Key={"id": {"S": unit_id}},
        UpdateExpression="SET information.details.#is_shared = :new_value",
        ExpressionAttributeNames={
            "#is_shared": "shared"
        },
        ExpressionAttributeValues={":new_value": {"BOOL": True}},
        ReturnValues="UPDATED_NEW",
    )

    update_shared_with = dynamo.update_item(
        TableName=UNITS_TABLE_ARN,
        Key={"id": {"S": unit_id}},
        UpdateExpression="SET information.details.shared_with = list_append(if_not_exists(shared_with, :empty_list), :new_value)",
        ExpressionAttributeValues={
            ":new_value": {"L": [{"S": user}]},
            ":empty_list": {'L': []}
        },
        ReturnValues="UPDATED_NEW",
    )

    return (update_shared_bool, update_shared_with)


def get_unit_index_from_client_table(client, unit_id):
    client_response = dynamo.query(
        TableName=CLIENTS_TABLE_ARN,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {
                'S': client
            }
        }
    )
    unit_list = client_response["Items"][0]["units"]["L"]
    unit_index = 0
    for unit in unit_list:
        if unit_id == unit["M"]["unit_id"]["S"]:
            return unit_index
        else:
            unit_index += 1

    raise Exception(f"Unit with id: {unit_id} not found in client: {client}")


def update_clients_table(client, unit_id, user):
    unit_index = get_unit_index_from_client_table(client, unit_id)
    expression = f"""
        SET units[{unit_index}].shared_with = list_append(if_not_exists(units[{unit_index}].shared_with, :empty_list), :new_sharing_value)
    """
    update_shared_with = dynamo.update_item(
        TableName=CLIENTS_TABLE_ARN,
        Key={"id": {"S": client}},
        UpdateExpression=expression,
        ExpressionAttributeValues={
            ":new_sharing_value": {
                "L": [{
                    "S": user
                }]
            },
            ":empty_list": {"L": []}
        },
        ReturnValues="UPDATED_NEW"
    )

    update_shared_bool = dynamo.update_item(
        TableName=CLIENTS_TABLE_ARN,
        Key={
            'id': {'S': client}
        },
        UpdateExpression=f"SET units[{unit_index}].#is_shared = :new_sharing_bool",
        ExpressionAttributeNames={
            "#is_shared": "shared"
        },
        ExpressionAttributeValues={
            ":new_sharing_bool": {'BOOL': True}
        },
        ReturnValues="UPDATED_NEW"
    )

    return (update_shared_with, update_shared_bool)


def lambda_handler(event, context):
    response_body = {"Message": "get_client_units crashed"}
    status_code = 400
    headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}

    try:
        unit_id = event["unit_id"]
        client = event["client"]
        user = event["shared_with"]

        print("Writing to units table")
        unit_response = update_units_table(unit_id, user)
        print(f"Unit table update response: {str(unit_response)}")

        print("Writing to clients table")
        client_response = update_clients_table(client, unit_id, user)
        print(f"Client table update response: {str(client_response)}")

        status_code = 200
        response_body["Message"] = "Shared successfully"

    except Exception as err:
        print(str(err))
        response_body["Message"] = str(err)

    return {
        "statusCode": status_code,
        "body": json.dumps(response_body),
        "headers": headers,
    }
