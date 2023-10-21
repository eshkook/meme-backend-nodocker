import boto3
import json
import requests
import traceback  # <-- Make sure to import traceback
from boto3.dynamodb.conditions import Key

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_3_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'
edit_url = f'{api_url}/editMessageText'

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = None
        query_data = None
        
        if 'message' in body:
            chat_id = body['message']['chat']['id']
            user_message = body['message'].get('text', '')
            message_id = body['message']['message_id']
            if user_message == '/start':
                send_available_slots(chat_id, message_id)
            else:
                collapse_unused_slots(chat_id)
                shut_up_and_send_available_slots(chat_id, message_id)

        elif 'callback_query' in body:
            chat_id = body['callback_query']['message']['chat']['id']
            query_data = body['callback_query']['data']
            appointment_id = query_data  # Assuming the callback data is the appointment ID

            # get the chosen slot
            item = table.get_item(
                Key={'id': str(appointment_id)}
            )
            item = item.get('Item')
            message_id = body['callback_query']['message']['message_id']

            if item["is_available"]:
                # Update the selected slot to mark it as unavailable
                table.update_item(
                    Key={
                        'id': appointment_id,
                    },
                    UpdateExpression="SET is_available = :false",
                    ExpressionAttributeValues={':false': False}
                )
                response_text = f"You selected: {item['appointment_times']}. See you soon!"
                new_message_text = f"Hello! Let's schedule an appointment. Please choose one of the available slots:\n\n{response_text}"
                
                payload = {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': new_message_text
                }
                response = requests.post(edit_url, json=payload)
            else:
                send_available_slots_again(chat_id, message_id) 
        
        return {"statusCode": 200}
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # New logging statement to print the stack trace
        return {"statusCode": 200}
        
def fetch_available_slots():
    response = table.scan(
        FilterExpression=Key('is_available').eq(True) # a linear time search
    )
    available_slots = response.get('Items', [])
    sorted_slots = sorted(available_slots, key=lambda x: x['appointment_times'])
    return sorted_slots

def send_available_slots(chat_id, message_id):
    available_slots = fetch_available_slots()
    if available_slots:
        keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
        payload = {
            'chat_id': chat_id,
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
        table.put_item(
            Item={
                'id': str(chat_id),
                'message_id': message_id
            }
        )
    else:
        payload = {
            'chat_id': chat_id,
            'text': "Sorry, no available slots at the moment."
        }
    response = requests.post(f'{api_url}/sendMessage', json=payload)

def shut_up_and_send_available_slots(chat_id, message_id):
    available_slots = fetch_available_slots()
    if available_slots:
        keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
        payload = {
            'chat_id': chat_id,
            'text': "Who said you can talk? Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
        table.put_item(
            Item={
                'id': str(chat_id),
                'message_id': message_id
            }
        )
    else:
        payload = {
            'chat_id': chat_id,
            'text': "Who said you can talk? Sorry, no available slots at the moment."
        }     
    response = requests.post(f'{api_url}/sendMessage', json=payload)    

def send_available_slots_again(chat_id, message_id):
    available_slots = fetch_available_slots()
    if available_slots:
        keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nThat slot was already taken! Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
        table.put_item(
            Item={
                'id': str(chat_id),
                'message_id': message_id
            }
        )
    else:
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nThat slot was already taken! Sorry, no available slots at the moment."
        }   
    response = requests.post(edit_url, json=payload)

def collapse_unused_slots(chat_id):
    item = table.get_item(
                Key={'id': str(chat_id)}
            )
    item = item.get('Item')
    message_id = item["message_id"]
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nYou didn''t pick a slot.",
    }
   
    response = requests.post(edit_url, json=payload)    
