import boto3
import json
import requests
from datetime import datetime

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_2_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = body['message']['chat']['id']
        user_message = body['message'].get('text', '')

        # Fetch existing conversation
        response = table.get_item(
            Key={'id': str(chat_id)}
        )
        item = response.get('Item')

        if item:
            # Existing conversation
            conversation = item['conversation']
            if len(conversation) == 1:
                bot_reply = 'keep talking'
            else:
                bot_reply = conversation[-2]["message"]

            # Update conversation
            conversation.extend([{"entity": "user",
                                "message": user_message}],
                                [{"entity": "bot",
                                "message": bot_reply}])    
        else:
            # New conversation
            bot_reply = 'Hellow!'
            conversation = [{"entity": "bot",
                             "message": "Hellow!"}]

        
        table.put_item(
            Item={
                'id': str(chat_id),
                'conversation': conversation
            }
        )

        # Send reply
        payload = {
            'chat_id': chat_id,
            'text': bot_reply
        }
        response = requests.post(f'{api_url}/sendMessage', json=payload)

        return {"statusCode": 200}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"statusCode": 200}
