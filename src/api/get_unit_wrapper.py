'''
This is our wrapper for the GET /units

Using this to trigger other functions based on request

We will allow the following request-end-points:
    - type: client
        > get_client_units.py
    - type: unit_id
        > get_unit.py
    - type: state
        > get_units.py
'''

import json
import boto3
import os


# Building client for lambda invokation
lambda_client = boto3.client('lambda')

# Declaring function ARN's
GET_UNITS_STATE = os.getenv('GETUNITS_FUNCTION_ARN')
GET_UNITS_CLIENT = os.getenv('GETCLIENTUNITS_FUNCTION_ARN')
GET_UNIT_ID = os.getenv('GETUNIT_FUNCTION_ARN')


def validate_body(body, type):
    if type not in body:
        raise Exception(f"Invalid parameters. '{type}' not found.")


def invoke_lambda(function_arn:str, payload:dict):
    print(f"Invoking function: {function_arn}, with payload: {payload}")
    return lambda_client.invoke(
        FunctionName=function_arn,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )


def lambda_handler(event, context):

    print(f"GET_UNITS_STATE: {GET_UNITS_STATE}")
    print(f"GET_UNITS_CLIENT: {GET_UNITS_CLIENT}")
    print(f"GET_UNIT_ID: {GET_UNIT_ID}")

    # default response
    response_body = {'Message': 'get_unit_wrapper crashed'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_params = event.get('queryStringParameters', {})
        print(str(request_params))

        if not request_params:
            print("request_params not valid")
            raise Exception("Invalid Request. No paramaters parsed.")

        # validating the request body has type
        if "type" not in request_params:
            print("type not in request_params not valid")
            raise Exception("Invalid request. 'type' not in body.")
        else:
            type = request_params['type']

        print("validating request_params")
        validate_body(request_params, type)

        # Invoke different functions based on their request
        if type == 'client':
            response = invoke_lambda(GET_UNITS_CLIENT, {
                'client': request_params['client']
            })
        elif type == 'state' or type == 'rent' and 'location' in request_params or 'size' in request_params:
            response = invoke_lambda(GET_UNITS_STATE, {
                'state': 'available',
                'location': request_params['location'],
                'size': request_params['size'].lower()
            })
        elif type == 'state':
            response = invoke_lambda(GET_UNITS_STATE, {
                'state': request_params['state']
            })
        elif type == 'unit_id':
            response = invoke_lambda(GET_UNIT_ID, {
                'unit_id': request_params['unit_id']
            })
        elif type == 'rent':
            response = invoke_lambda(GET_UNITS_STATE, {
                'state': 'available',
                'location': request_params['location'],
                'size': request_params['size'].lower()
            })
        else:
            raise Exception(f"Invalid request. '{type}' requested is invalid.")

        print(str(response))
        # print(str(json.load(response)))
        # payload = json.load(dict(response['Payload']))
        # stream_payload = response["Payload"]

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
