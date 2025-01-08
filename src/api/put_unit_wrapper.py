'''
This is our wrapper for the PUT /units

Using this to trigger other functions based on request

We will allow the following request-end-points:

    change:
        - payment_method
            > change_billing.py
            > CHANGEBILLING_FUNCTION_ARN
        - cancel
            > cancel.py
            > CANCELLEASE_FUNCTION_ARN
        - extended
            > extend.py
            > EXTENDDEADLINE_FUNCTION_ARN
        - open
            > open_unit.py
            > OPENUNIT_FUNCTION_ARN
        - shared
            > share_unit.py
            > SHAREUNIT_FUNCTION_ARN
        - stop_sharing
            > stop_sharing.py
            > STOPSHARING_FUNCTION_ARN


'''

import json
import boto3
import os


# Building client for lambda invokation
lambda_client = boto3.client('lambda')

# Declaring function ARN's
SHAREUNIT_FUNCTION_ARN = os.getenv('SHAREUNIT_FUNCTION_ARN')
CHANGEBILLING_FUNCTION_ARN = os.getenv('CHANGEBILLING_FUNCTION_ARN')
CANCELLEASE_FUNCTION_ARN = os.getenv('CANCELLEASE_FUNCTION_ARN')
EXTENDDEADLINE_FUNCTION_ARN = os.getenv('EXTENDDEADLINE_FUNCTION_ARN')
OPENUNIT_FUNCTION_ARN = os.getenv('OPENUNIT_FUNCTION_ARN')
STOPSHARING_FUNCTION_ARN = os.getenv('STOPSHARING_FUNCTION_ARN')


def raiseException(key, change):
    raise Exception(
        f"Invalid request. '{key}' not present in the {change} changeset."
    )

def switch_invoke_details(change_set: dict, change: str, unit_id: str):
    # Invoke different functions based on their request

    if change == "payment_type":
        print('filtered correctly') 
        function_arn = CHANGEBILLING_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "value": change_set["value"],
            "client": change_set["client"]
        }
        

    elif change == "state":
        function_arn = CANCELLEASE_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "value": change_set["value"]
        }

    elif change == "end_date":
        function_arn = EXTENDDEADLINE_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "end_date": change_set["value"],
            "client": change_set["client"]
        }

    elif change == "open":
        function_arn = OPENUNIT_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "client": change_set["client"]
        }
    elif change == "shared":
        function_arn = SHAREUNIT_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "shared_with": change_set["value"],
            "client": change_set["client"]
        }
    elif change == "stop_sharing":
        function_arn = STOPSHARING_FUNCTION_ARN
        payload = {
            "unit_id": unit_id,
            "shared_with": change_set["value"],
            "client": change_set["client"]
        }
    else:
        raise Exception(f"Invalid request. '{type}' requested is invalid.")

    return function_arn, payload


def validate_body(change_set):
    if "value" not in change_set:
        raiseException("value", change_set)


def invoke_lambda(function_arn: str, payload: dict):
    print(f"Invoking function: {function_arn}, with payload: {payload}")
    return lambda_client.invoke(
        FunctionName=function_arn,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )


def lambda_handler(event, context):

    # default response
    response_body = {'Message': 'put_unit_wrapper crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_body = json.loads(event['body'])
        print(str(request_body))

        if not request_body:
            print("Request body not valid: " + str(request_body))
            raise Exception("Invalid Request. No paramaters parsed.")

        # validation request_body has unit_id
        if "unit_id" not in request_body:
            print("unit_id not specified in request_body: " + str(request_body))
            raise Exception("Invalid request. No unit_id specified.")
        else:
            unit_id = request_body["unit_id"]

        # validating the request body has type
        if "changeset" not in request_body:
            print("changeset not in request_body: " + str(request_body))
            raise Exception("Invalid request. 'changeset' not in body.")
        else:
            change_set = request_body["changeset"]

        if "change" not in change_set:
            print("change not in changeset: " + str(change_set))
            raise Exception("Invalid request. 'change' not in changeset.")
        else:
            change = change_set["change"]

        print("validating changeset")
        validate_body(change_set)

        print("switching invoke details")
        function_arn, payload = switch_invoke_details(
            change_set, change, unit_id
        )
        print(f"function_arn: {function_arn}, payload: {str(payload)}")

        print("Invoking wrapped function")
        response = invoke_lambda(function_arn, payload)

        print(str(response))

        # payload = stream_payload.read()
        payload = json.load(response["Payload"])
        print(f"Payload: {str(payload)}")

        status_code = payload['statusCode']
        response_body = payload['body']

    except Exception as err:
        response_body = {
            'Message': str(err),
        }

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
