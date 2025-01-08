import json
import os
import boto3


# Environment variables
USER_POOL_ID = os.getenv("USER_POOL_ID")
USER_POOL_CLIENT_ID = os.getenv("USER_POOL_CLIENTID")
USER_GROUP = os.getenv("DEFAULT_GROUP")
CLIENT_TABLE_NAME = os.getenv("CLIENTS_TABLE_NAME")
DEFAULT_PASSWORD = "Default@123"


cognito_client = boto3.client("cognito-idp")
user_table = boto3.resource("dynamodb").Table(CLIENT_TABLE_NAME)


def create_user(email, password) -> tuple[int, str]:
    print("Creating cognito user")
    try:
        # create user
        print("Creating user")
        cognito_client.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=email,
            TemporaryPassword=DEFAULT_PASSWORD,
            MessageAction="SUPPRESS"
        )
        print("Created user")

        # set password
        print("Setting user password")
        cognito_client.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=email,
                Password=password,
                Permanent=True
        )
        print("Set password")

        # add user to grouop
        print("Adding user to group")
        cognito_client.admin_add_user_to_group(
                UserPoolId=USER_POOL_ID,
                Username=email,
                GroupName=USER_GROUP
        )
        print("Added user")

        print("Created user successfully, proceeding to add to db")
        return (200, "User created successfully")

    except cognito_client.exceptions.UsernameExistsException:
        return (401, "Email already exists.")

    except Exception as e:
        print(str(e))
        return (500, str(e))


def add_user_to_user_database(args:dict):
    print("Adding user to client db")
    try:
        response = str(user_table.put_item(
            Item={
                "id": args["email"],
                "first_name": args["name"],
                "last_name": args["surname"],
                "location": args["location"],
                "phone_number": args["phone_number"]
            }
        ))
        
        print("Added user to client db")
        return 200, "Created Account Successfully"

    except Exception as err:
        print(str(response))
        print(str(err))
        return 401, str(err)


def lambda_handler(event, context):

    response_body = {'Message': 'Unsupported route'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
        }

    try:
        route_key = f"{event['httpMethod']} {event['resource']}"
        if route_key == "POST /create_user":
            request_json = json.loads(event['body'])

            if "email" not in request_json:
                raise Exception("Invalid Request" + str(request_json))
            else:
                email = str(request_json["email"])
                password = str(request_json["password"])
                status_code, message = create_user(email, password)

            if status_code == 200:
                # email = str(request_json["email"])
                args = {
                    "email": email,
                    "name": str(request_json["name"]),
                    "surname": str(request_json["surname"]),
                    "location": str(request_json["location"]),
                    "phone_number": str(request_json["phone_number"])
                }
                status_code, message = add_user_to_user_database(args)
            response_body['Message'] = message

    except Exception as err:
        status_code = 400
        response_body = {'Error:': str(err)}
        # print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
