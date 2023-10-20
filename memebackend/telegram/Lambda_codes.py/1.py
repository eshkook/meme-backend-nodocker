import boto3
import json
import requests
import traceback  # <-- Make sure to import traceback
from boto3.dynamodb.conditions import Key

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'

def lambda_handler(event, context):
    text = None
    try:
        body = json.loads(event['body'])
        chat_id = None
        query_data = None
        
        if 'message' in body:
            chat_id = body['message']['chat']['id']
            text = body['message'].get('text', '')
        elif 'callback_query' in body:
            chat_id = body['callback_query']['message']['chat']['id']
            query_data = body['callback_query']['data']
        
        if text and text.lower() == '/start':
            send_available_slots(chat_id)
            
        elif query_data:
            appointment_id = query_data  # Assuming the callback data is the appointment ID
            selected_slot = next((slot for slot in fetch_available_slots() if slot['id'] == appointment_id), None)
            if selected_slot:
                # Update the selected slot to mark it as unavailable
                table.update_item(
                    Key={
                        'id': appointment_id,
                        'timestamp': selected_slot['timestamp']  # assuming selected_slot has a 'timestamp' field
                    },
                    UpdateExpression="SET is_available = :false",
                    ExpressionAttributeValues={':false': False}
                )
                print("Update successful")  # New logging statement
                response_text = f"You selected: {selected_slot['appointment_times']}. See you soon!"
                new_message_text = f"Hello! Let's schedule an appointment. Please choose one of the available slots:\n\n{response_text}"
                edit_url = f'{api_url}/editMessageText'
                payload = {
                    'chat_id': chat_id,
                    'message_id': body['callback_query']['message']['message_id'],
                    'text': new_message_text
                }
                response = requests.post(edit_url, json=payload)
        
        return {"statusCode": 200}
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # New logging statement to print the stack trace
        return {"statusCode": 200}
        
def send_available_slots(chat_id):
    available_slots = fetch_available_slots()
    if available_slots:
        keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
        payload = {
            'chat_id': chat_id,
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
    else:
        payload = {
            'chat_id': chat_id,
            'text': "Sorry, no available slots at the moment."
        }
    response = requests.post(f'{api_url}/sendMessage', json=payload)

def process_slot_selection(chat_id, slot_id):
    mark_slot_unavailable(slot_id)
    slot_time = fetch_slot_time(slot_id)
    payload = {
        'chat_id': chat_id,
        'text': f'You selected: {slot_time}. See you soon!'
    }
    response = requests.post(f'{api_url}/sendMessage', json=payload)

def fetch_available_slots():
    response = table.scan(
        FilterExpression=Key('is_available').eq(True)
    )
    available_slots = response.get('Items', [])
    sorted_slots = sorted(available_slots, key=lambda x: x['timestamp'])
    return sorted_slots

def mark_slot_unavailable(slot_id):
    table.update_item(
        Key={'id': slot_id},
        UpdateExpression="SET is_available = :val",
        ExpressionAttributeValues={':val': False}
    )

def fetch_slot_time(slot_id):
    response = table.get_item(
        Key={'id': slot_id}
    )
    return response['Item']['appointment_times']
