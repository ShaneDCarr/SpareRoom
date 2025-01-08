import os
import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

# Environment variables
USER_POOL_ID = os.getenv("USERPOOL_ID")
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
REGION = "eu-west-1"
ADMIN_GROUP_NAME = os.getenv("ADMIN_GROUP_NAME", "Admins")
CUSTOMER_GROUP_NAME = os.getenv("CUSTOMER_GROUP_NAME", "Customers")

# Caching keys for efficiency
keys_cache = None


def fetch_jwks():
    """Fetch JWKS keys from Cognito."""
    global keys_cache
    if not keys_cache:
        try:
            print(REGION)
            print(USER_POOL_ID)
            url = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
            print(f"Fetching JWT keys from: {url}")
            with urllib.request.urlopen(url) as response:
                keys_cache = json.loads(response.read())["keys"]
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTPError {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URLError: {e.reason}")
        except Exception as e:
            raise Exception(f"General Exception: {e}")
    return keys_cache


def validate_jwt(token):
    """Validates the JWT token."""
    keys = fetch_jwks()
    print(str(token))
    if "Bearer" in token:
        token = token.split(" ")[1]
        print("formatted token" + token)
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")

    # Find the public key for the token's kid
    key = next((k for k in keys if k["kid"] == kid), None)
    if not key:
        raise Exception("Unauthorized: Key not found")

    # Verify the token
    public_key = jwk.construct(key)
    message, encoded_signature = token.rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise Exception("Unauthorized: Signature verification failed")

    # Decode claims and verify
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims["exp"]:
        raise Exception("Unauthorized: Token expired")
    if claims["aud"] != APP_CLIENT_ID:
        raise Exception("Unauthorized: Invalid audience")

    return claims


def all_unit_resources(arn: str):

    arn_split = arn.split(":")
    path = arn_split[5].split("/")[0]
    resource = ":".join([arn_split[i] for i in range(5)])
    return resource + ":" + path + "/*/units"


def get_rent_resources(arn: str):
    arn_split = arn.split(":")
    path = arn_split[5].split("/")[0]
    resource = ":".join([arn_split[i] for i in range(5)])

    return [
        resource + ":" + path + "/*/rent",
        # resource + ":" + path + "/OPTIONS/rent",
    ]


def get_notification_resources(arn: str):
    arn_split = arn.split(":")
    path = arn_split[5].split("/")[0]
    resource = ":".join([arn_split[i] for i in range(5)])

    return [
        resource + ":" + path + "/GET/notifications",
        resource + ":" + path + "/OPTIONS/notifications"
    ]


def all_notification_resources(arn: str):
    arn_split = arn.split(":")
    path = arn_split[5].split("/")[0]
    resource = ":".join([arn_split[i] for i in range(5)])

    return resource + ":" + path + "/*/notifications"


def generate_customer_policy(principal_id, effect, resource):
    """Generates an IAM policy document."""

    all_resource = [arn for arn in get_rent_resources(resource)]
    all_resource.append(all_unit_resources(resource))
    all_resource.append(all_notification_resources(resource))
    resource = all_resource

    response = {
                "principalId": principal_id,
                "policyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                                    "Action": "execute-api:Invoke",
                                    "Effect": effect,
                                    "Resource": resource,
                                }]
                }
    }

    print("Response: " + str(response))

    return response


def generate_basic_policy(principal_id, effect, resource):
    """Generates an IAM policy document."""

    response = {
                "principalId": principal_id,
                "policyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                                    "Action": "execute-api:Invoke",
                                    "Effect": effect,
                                    "Resource": resource,
                                }]
                }
    }

    print("Response: " + str(response))

    return response


def lambda_handler(event, context):
    token = event["authorizationToken"]
    method_arn = event["methodArn"]

    print(f'event: {event}')
    print(f'token: {token}')
    print(f'context: {context}')
    print(f"Authorization Token: {event.get('authorizationToken')}")
    print(f"Method ARN: {event.get('methodArn')}")

    try:
        claims = validate_jwt(token)
        user_id = claims["sub"]
        roles = claims.get("cognito:groups", [])
        print(roles)

        # Allow access for admins
        if ADMIN_GROUP_NAME in roles:
            print("creating admin role")
            return generate_customer_policy(user_id, "Allow", method_arn)

        # Allow access for customers
        if CUSTOMER_GROUP_NAME in roles:
            print("creating customer role")
            return generate_customer_policy(user_id, "Allow", method_arn)

        # Allow users to access their own resources
        # if "users" in method_arn and f"/{user_id}" in method_arn:
        #     return generate_policy(user_id, "Allow", method_arn)

        # Deny by default
        return generate_basic_policy(user_id, "Deny", method_arn)

    except Exception as e:
        print(f"Authorization failed: {e}")
        raise Exception("Unauthorized")
