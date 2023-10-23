import boto3
import json
import requests
import traceback  
from boto3.dynamodb.conditions import Key
import decimal

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_3_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'
sendMessage_url = f'{api_url}/sendMessage'
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

            item = table.get_item(
                Key={'id': str(chat_id)}
            )
            item = item.get('Item')

            if item and item["canceling_options_message_id"]:
                old_message_id = item["canceling_options_message_id"]
                appointment_id = item['appointment_id']
                item = table.get_item(
                    Key={'id': str(appointment_id)}
                )
                item = item.get('Item')
                appointment_times = item['appointment_times']
                payload = {
                    'chat_id': str(chat_id),
                    'message_id': int(old_message_id),
                    'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou didn't select any option.",
                }
                response = requests.post(edit_url, json=payload)

                ask_to_cancel_appointment(chat_id, appointment_id)
                table.update_item(
                Key={
                    'id': str(chat_id),
                    },
                    UpdateExpression="SET canceling_options_message_id = :message_id",
                    ExpressionAttributeValues={':message_id': message_id}
                )

            else:    
                # check if the user already has an appointment:
                appointment_id = item.get('appointment_id') if item else None                
                if appointment_id: # then the user already has an appointment scheduled
                    ask_to_cancel_appointment(chat_id, appointment_id)
                    table.update_item(
                    Key={
                        'id': str(chat_id),
                        },
                        UpdateExpression="SET message_id = :message_id",
                        ExpressionAttributeValues={':message_id': message_id}
                    )
                else:
                    if item:
                        collapse_unused_slots(chat_id)

                    send_available_slots(chat_id, message_id)
                
        elif 'callback_query' in body:
            chat_id = body['callback_query']['message']['chat']['id']
            query_data = body['callback_query']['data']
            message_id = body['callback_query']['message']['message_id']

            if query_data == 'keep':
                # check when is the appointment:
                item = table.get_item(
                    Key={'id': str(chat_id)}
                )
                item = item.get('Item')
                appointment_id = item.get('appointment_id')
                item = table.get_item(
                    Key={'id': appointment_id}
                )
                item = item.get('Item')
                appointment_times = item.get('appointment_times')
                payload = {
                    'chat_id': str(chat_id),
                    'message_id': int(message_id),
                    'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou selected: Keep the appointment.",
                }
                response = requests.post(edit_url, json=payload)

                payload = {
                    'chat_id': str(chat_id),
                    'text': f"Your appointment is kept. See you soon!",
                }
                response = requests.post(sendMessage_url, json=payload)

            elif query_data == 'cancel':
                # check when is the appointment:
                item = table.get_item(
                    Key={'id': str(chat_id)}
                )
                item = item.get('Item')
                appointment_id = item.get('appointment_id')
                item = table.get_item(
                    Key={'id': appointment_id}
                )
                item = item.get('Item')
                appointment_times = item.get('appointment_times')

                # edit the earlier message
                payload = {
                    'chat_id': str(chat_id),
                    'message_id': int(message_id),
                    'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou selected: Cancel the appointment.",
                }
                response = requests.post(edit_url, json=payload)

                payload = {
                    'chat_id': str(chat_id),
                    'text': f"Your appointment has been canceled. Have a great day!",
                }
                response = requests.post(sendMessage_url, json=payload)

                # Update the selected slot to mark it as available:
                table.update_item(
                    Key={
                        'id': appointment_id,
                    },
                    UpdateExpression="SET is_available = :true",
                    ExpressionAttributeValues={':true': True}
                )
                # delete chat_id from DB:
                table.delete_item(
                    Key={
                        'id': str(chat_id)
                    }
                )

            elif query_data == 'reschedule':
                # check when is the appointment:
                item = table.get_item(
                    Key={'id': str(chat_id)}
                )
                item = item.get('Item')
                appointment_id = item.get('appointment_id')
                item = table.get_item(
                    Key={'id': appointment_id}
                )
                item = item.get('Item')
                appointment_times = item.get('appointment_times')

                # Update the selected slot to mark it as available:
                table.update_item(
                    Key={
                        'id': appointment_id,
                    },
                    UpdateExpression="SET is_available = :true",
                    ExpressionAttributeValues={':true': True}
                )

                # Update the chat_id:
                table.update_item(
                    Key={
                        'id': str(chat_id),
                    },
                    UpdateExpression="SET appointment_id = :none",
                    ExpressionAttributeValues={':none': None}
                )

                # edit the earlier message
                available_slots = fetch_available_slots()
                payload = {
                    'chat_id': str(chat_id),
                    'message_id': int(message_id),
                    'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou selected: Reschedule the appointment.",
                    
                }
                response = requests.post(edit_url, json=payload)

                keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
                payload = {
                    'chat_id': str(chat_id),
                    'text': f"Hellow! Let's schedule an appointment. Please choose one of the available slots:",
                    'reply_markup': {"inline_keyboard": keyboard}
                }
                response = requests.post(sendMessage_url, json=payload)

            else:   
                appointment_id = query_data  # Assuming the callback data is the appointment ID
                message_id = body['callback_query']['message']['message_id']
                schedule_appointment(chat_id, appointment_id, message_id) 
        
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
        text = "Hello! Let's schedule an appointment. Please choose one of the available slots:"   
        payload = {
            'chat_id': str(chat_id),
            'text': text,
            'reply_markup': {"inline_keyboard": keyboard}
        }
        response = requests.post(sendMessage_url, json=payload)
        table.put_item(
            Item={
                'id': str(chat_id),
                'message_id': str(message_id),
                'appointment_id': None
            }
        )
    else:
        payload = {
            'chat_id': chat_id,
            'text': "Sorry, no available slots at the moment."
        }
        response = requests.post(sendMessage_url, json=payload)   

def send_available_slots_again(chat_id, message_id):
    available_slots = fetch_available_slots()
    if available_slots:
        keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
        payload = {
            'chat_id': str(chat_id),
            'message_id': str(message_id),
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nThat slot was already taken! Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
        response = requests.post(sendMessage_url, json=payload)
        table.put_item(
            Item={
                'id': str(chat_id),
                'message_id': str(message_id),
                'appointment_id': None,
                'canceling_options_message_id': None 
            }
        )
    else:
        payload = {
            'chat_id': str(chat_id),
            'message_id': str(message_id),
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
        'chat_id': str(chat_id),
        'message_id': int(message_id),
        'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nYou didn't pick a slot.",
    }
    response = requests.post(edit_url, json=payload)
    print(99999999999999)
    print(response.json())
    print(99999999999999)
     
def ask_to_cancel_appointment(chat_id, appointment_id):
    item = table.get_item(
        Key={'id': appointment_id}
    )
    item = item.get('Item')
    appointment_times = item["appointment_times"]
    print("appointment_times:", appointment_times)
    keyboard = [
                    [{"text": "Keep the appointment", "callback_data": 'keep'}],
                    [{"text": "Cancel the appointment", "callback_data": 'cancel'}],
                    [{"text": "Reschedule the appointment", "callback_data": 'reschedule'}]
                ]
    payload = {
        'chat_id': str(chat_id),
        'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:",
        'reply_markup': {"inline_keyboard": keyboard}
    }
    response = requests.post(sendMessage_url, json=payload)
        
def schedule_appointment(chat_id, appointment_id, message_id): 
    # get the chosen slot
    item = table.get_item(
        Key={'id': str(appointment_id)}
    )
    item = item.get('Item')

    if item["is_available"]:
        response_text = f"You selected: {item['appointment_times']}. See you soon!"
        new_message_text = f"Hello! Let's schedule an appointment. Please choose one of the available slots:\n\n{response_text}"
        
        payload = {
            'chat_id': str(chat_id),
            'message_id': str(message_id),
            'text': new_message_text
        }
        response = requests.post(edit_url, json=payload)

        table.update_item(
            Key={
                'id': appointment_id,
            },
            UpdateExpression="SET is_available = :false, chat_id = :chat_id",
            ExpressionAttributeValues={
                ':false': False,
                ':chat_id': str(chat_id)  
            }
        )

        table.update_item(
            Key={
                'id': str(chat_id),
            },
            UpdateExpression="SET appointment_id = :appointment_id",
            ExpressionAttributeValues={
                ':appointment_id': appointment_id
            }
        )
    else:
        send_available_slots_again(chat_id, message_id)