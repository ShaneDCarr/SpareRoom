import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

table_name = 'Notifications'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    unit_id = event['queryStringParameters'].get('unit_id')

    if not unit_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error', 'unit id is required'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    try:
        response = table.get_item(Key={'unit_id': unit_id})
        item = response.get('Item', {})
        notifications = item.get('notifications', [])
        if notifications:
            notifications = notifications[::-1]

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(notifications)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
