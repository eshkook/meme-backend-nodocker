import boto3
import json
import requests
from datetime import datetime

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = body['message']['chat']['id']
        user_text = body['message'].get('text', '')
        
        response = table.get_item(
            Key={'id': chat_id}
        )
        item = response.get('Item')
        if item:
            bot_response = item['conversation'][-1].split(': ')[1] if len(item['conversation']) > 1 else 'keep talking'
            conversation = item['conversation'] + [f'user: {user_text}', f'bot: {bot_response}']
        else:
            bot_response = 'Hellow!'
            conversation = [f'bot: {bot_response}']
        
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        table.put_item(
            Item={
                'id': chat_id,
                'timestamp': timestamp,
                'conversation': conversation
            }
        )
        
        payload = {
            'chat_id': chat_id,
            'text': bot_response
        }
        response = requests.post(f'{api_url}/sendMessage', json=payload)
        
        return {"statusCode": 200}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"statusCode": 200}
