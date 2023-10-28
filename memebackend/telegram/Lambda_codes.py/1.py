import boto3
import json
import requests
import traceback  
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta
import dateutil.tz

# AWS DynamoDB setup
region_name = 'eu-west-1'
table_name = 'botox_3_table'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)
israel_tz = dateutil.tz.gettz('Asia/Jerusalem')

# Telegram setup
telegram_token = '6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg'
api_url = f'https://api.telegram.org/bot{telegram_token}'
sendMessage_url = f'{api_url}/sendMessage'
edit_url = f'{api_url}/editMessageText'
delete_url = f'{api_url}/deleteMessage'

def lambda_handler(event, context):
    try:
        # Check if the event is from CloudWatch
        if 'source' in event and event['source'] == 'aws.events':
            handle_cloudwatch_event(event)
        else:
            handle_telegram_event(event)
        return {"statusCode": 200}
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return {"statusCode": 200}

def handle_cloudwatch_event(event): # call every round hour between 8:00-17:00 inclusive
    current_time = datetime.now(israel_tz)

    # 1. sending an alert to a user about an upcomming appointment
    if current_time.strftime("%H") <= 16:
        next_round_hour_time = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        next_round_hour_time = next_round_hour_time.strftime("%Y-%m-%d %H:%M")
        item = table.get_item(
            Key={'id': next_round_hour_time}
        )
        item = item.get('Item')
        chat_id = item.get('chat_id')
        appointment_times = item.get('appointment_times')
        payload = {
            'chat_id': str(chat_id),
            'text': f"Hi! We remind you that your appointment is at {appointment_times}. See you soon!",
        }
        response = requests.post(sendMessage_url, json=payload)

    # 2. drop the outdated slot 
    if current_time.strftime("%H") >= 9: 
        last_round_hour_time = current_time.replace(minute=0, second=0, microsecond=0)
        last_round_hour_time = last_round_hour_time.strftime("%Y-%m-%d %H:%M")
        table.delete_item(
        Key={
            'id': last_round_hour_time
            }
        )

    # 3. add next day's slots: (only at 8:00)
    if current_time.strftime('%A') != "Thursday" and current_time.strftime("%H") == 8:
        today_at_8_datetime = current_time.replace(hour=8, minute=0, second=0, microsecond=0) 
        tomorrow_at_8_datetime = today_at_8_datetime + timedelta(days=1)
        slots_list = [tomorrow_at_8_datetime + timedelta(hours=work_hours+1) for work_hours in range(9)]
        for slot in slots_list:
            table.put_item(
                Item={
                    'id': slot.strftime('%Y-%m-%d %H:%M'),
                    'is_available': True,
                    'chat_id': None,
                    'username': None,
                    'full_name': None,
                    'appointment_times': slot.strftime('%Y-%m-%d %H:%M') + '-' + (slot + timedelta(hours=1)).strftime('%H:%M')
                }
            )  
    if current_time.strftime('%A') == "Thursday" and current_time.strftime("%H") == 8:
        today_at_8_datetime = current_time.replace(hour=8, minute=0, second=0, microsecond=0) 
        next_sunday_at_8_datetime = today_at_8_datetime + timedelta(days=3)
        slots_list = [next_sunday_at_8_datetime + timedelta(hours=work_hours+1) for work_hours in range(9)]
        for slot in slots_list:
            table.put_item(
                Item={
                    'id': slot.strftime('%Y-%m-%d %H:%M'),
                    'is_available': True,
                    'chat_id': None,
                    'username': None,
                    'full_name': None,
                    'appointment_times': slot.strftime('%Y-%m-%d %H:%M') + '-' + (slot + timedelta(hours=1)).strftime('%H:%M')
                }
            )         

    # 4. delete 2 working days ago chats and close their open suggestions: (only at 17:00) 
    if current_time.strftime('%A') != "Sunday" and current_time.strftime("%H") == 17:
        two_days_ago_time_str = (current_time - timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
        delete_items_and_close_suggestions(two_days_ago_time_str)

    if current_time.strftime('%A') == "Sunday" and current_time.strftime("%H") == 17:
        four_days_ago_time_str = (current_time - timedelta(days=4)).strftime('%Y-%m-%d %H:%M')
        delete_items_and_close_suggestions(four_days_ago_time_str)    

def delete_items_and_close_suggestions(x_days_ago_time_str):
    # Initial scan
    response = table.scan(
        FilterExpression=Attr('recent_use_timestamp').lt(x_days_ago_time_str)
    )
    handle_items_from_response(response)

    # Continue scanning and deleting until all pages have been processed
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            FilterExpression=Attr('recent_use_timestamp').lt(x_days_ago_time_str),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        handle_items_from_response(response)

def handle_items_from_response(response):
    for item in response['Items']:
        if item['message_id']:
            print(f"Deleting open suggestion of chat id {item['id']}")
            old_message_id = item["message_id"]
            payload = {
                'chat_id': str(item['id']),
                'message_id': int(old_message_id),
                'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nYou didn't pick a slot.",
            }
            response = requests.post(edit_url, json=payload)

        if item["canceling_options_message_id"]:
            old_message_id = item["canceling_options_message_id"]
            appointment_times = item['appointment_times']
            payload = {
                'chat_id': str(item['chat_id']),
                'message_id': int(old_message_id),
                'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou didn't select any option.",
            }
            response = requests.post(edit_url, json=payload)    

        print(f"Deleting chat id {item['id']}")
        table.delete_item(
            Key={
                'id': item['id'],
            }
        )

def handle_telegram_event(event):
    body = json.loads(event['body'])
    chat_id = None
    query_data = None
    
    if 'message' in body:
        chat_id = body['message']['chat']['id']
        user_message = body['message'].get('text', '')
        message_id = body['message']['message_id']
        user_info = body['message']['from']
        username = user_info.get('username', '')
        full_name = user_info.get('first_name', '') + " " + user_info.get('last_name', '')

        item = table.get_item(
            Key={'id': str(chat_id)}
        )
        item = item.get('Item')

        # check if there are unused appointment-canceling options
        if item and item["canceling_options_message_id"]:
            appointment_times = item['appointment_times']
            appointment_id = item['appointment_id']
            old_message_id = item["canceling_options_message_id"]
            payload = {
                'chat_id': str(chat_id),
                'message_id': int(old_message_id),
                'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou didn't select any option.",
            }
            response = requests.post(edit_url, json=payload)

            if user_message == 'admin': 
                show_data_to_admin(chat_id)
            # check if we allow canceling (if there is more than 1 hour until appointment)
            elif (datetime.strptime(appointment_id, '%Y-%m-%d %H:%M').replace(tzinfo=israel_tz) - datetime.now(israel_tz)).total_seconds() > 3600: 
                ask_to_cancel_appointment(chat_id, appointment_id)
            else:
                too_late_to_cancel_appointment(chat_id, appointment_id)
        else:
            if user_message == 'admin': 
                if item and item['message_id']:
                    collapse_unused_slots(chat_id)
                show_data_to_admin(chat_id)
            else:    
                # check if the user already has an appointment:
                appointment_id = item.get('appointment_id') if item else None                
                if appointment_id: # then the user already has an appointment scheduled
                    # check if we allow canceling (if there is more than 1 hour until appointment)
                    if (datetime.strptime(appointment_id, '%Y-%m-%d %H:%M').replace(tzinfo=israel_tz) - datetime.now(israel_tz)).total_seconds() > 3600:
                        ask_to_cancel_appointment(chat_id, appointment_id)
                    else:
                        too_late_to_cancel_appointment(chat_id, appointment_id)    
                else:
                    if item and item['message_id']:
                        collapse_unused_slots(chat_id)

                    send_available_slots(chat_id, username, full_name)
            
    elif 'callback_query' in body:
        chat_id = body['callback_query']['message']['chat']['id']
        query_data = body['callback_query']['data']
        message_id = body['callback_query']['message']['message_id']

        # check when is the appointment:
        item = table.get_item(
            Key={'id': str(chat_id)}
        )
        item = item.get('Item')
        appointment_id = item.get('appointment_id')
        username = item.get('username')
        full_name = item.get('full_name')

        if appointment_id:
            item = table.get_item( 
                Key={'id': appointment_id}
            )
            item = item.get('Item')
            appointment_times = item.get('appointment_times')

        if query_data == 'keep':
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

            table.update_item(
                Key={
                    'id': str(chat_id),
                },
                UpdateExpression="SET canceling_options_message_id = :none",
                ExpressionAttributeValues={':none': None}
            )

            payload = {
                'chat_id': str(chat_id),
                'text': f"Your appointment is kept. See you soon!",
            }
            response = requests.post(sendMessage_url, json=payload)

        elif query_data == 'cancel':
            # edit the earlier message
            payload = {
                'chat_id': str(chat_id),
                'message_id': int(message_id),
                'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou selected: Cancel the appointment.",
            }
            response = requests.post(edit_url, json=payload)

            # check if we allow canceling (if there is more than 1 hour until appointment)
            if (datetime.strptime(appointment_id, '%Y-%m-%d %H:%M').replace(tzinfo=israel_tz) - datetime.now(israel_tz)).total_seconds() > 3600:
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
                    UpdateExpression="SET is_available = :true, chat_id = :none",
                    ExpressionAttributeValues={':true': True,
                                            ':none': None}
                )
                # delete chat_id from DB:
                table.delete_item(
                    Key={
                        'id': str(chat_id)
                    }
                )
            else:
                too_late_to_cancel_appointment(chat_id, appointment_times)

        elif query_data == 'reschedule':
            # edit the earlier message
            payload = {
                'chat_id': str(chat_id),
                'message_id': int(message_id),
                'text': f"You already have a scheduled appointment at {appointment_times}. What would you like to do:\n\nYou selected: Reschedule the appointment.",
            }
            response = requests.post(edit_url, json=payload)

            # check if we allow canceling (if there is more than 1 hour until appointment)
            if (datetime.strptime(appointment_id, '%Y-%m-%d %H:%M').replace(tzinfo=israel_tz) - datetime.now(israel_tz)).total_seconds() > 3600:
                # Update the selected slot to mark it as available:
                table.update_item(
                    Key={
                        'id': appointment_id,
                    },
                    UpdateExpression="SET is_available = :true, chat_id = :none",
                    ExpressionAttributeValues={':true': True, ':none': None}
                )
                
                # Update the chat_id:
                table.update_item(
                    Key={
                        'id': str(chat_id),
                    },
                    UpdateExpression="SET appointment_id = :none, canceling_options_message_id = :none",
                    ExpressionAttributeValues={':none': None,
                                            ':none': None,
                                            }
                )
                send_available_slots(chat_id, username, full_name)
            else:
                too_late_to_cancel_appointment(chat_id, appointment_times)    

        else:  # then the callback data is the appointment ID 
            appointment_id = query_data  
            message_id = body['callback_query']['message']['message_id']
            schedule_appointment(chat_id, appointment_id, message_id)

    # update chat's timestamp:
    item = table.get_item(
        Key={'id': str(chat_id)}
    )
    item = item.get('Item')
    
    if item:
        table.update_item(
            Key={
                'id': str(chat_id),
            },
            UpdateExpression="SET recent_use_timestamp = :recent_use_timestamp",
            ExpressionAttributeValues={':recent_use_timestamp': datetime.now(israel_tz).strftime("%Y-%m-%d %H:%M")}
        )
        
def fetch_available_slots():
    response = table.scan(
        FilterExpression=Attr('is_available').eq(True) 
    )
    available_slots = response.get('Items', [])
    sorted_slots = sorted(available_slots, key=lambda x: x['appointment_times'])
    return sorted_slots

def send_available_slots(chat_id, username, full_name):
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
        response_dict = response.json()
        sent_message_id = response_dict['result']['message_id']
        table.put_item(
            Item={
                'id': str(chat_id),
                'username': username,
                'full_name': full_name,
                'recent_use_timestamp': datetime.now(israel_tz).strftime("%Y-%m-%d %H:%M"),
                'message_id': str(sent_message_id),
                'appointment_id': None,
                'appointment_times': None,
                'canceling_options_message_id': None 
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
            'message_id': int(message_id),
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nThat slot was already taken or expired! Please choose one of the available slots:",
            'reply_markup': {"inline_keyboard": keyboard}
        }
        response = requests.post(sendMessage_url, json=payload)

        response_dict = response.json()
        sent_message_id = response_dict['result']['message_id']
        table.update_item(
            Key={
                'id': str(chat_id),
            },
            UpdateExpression="SET message_id = :sent_message_id",
            ExpressionAttributeValues={':sent_message_id': str(sent_message_id)}
        )

    else:
        payload = {
            'chat_id': str(chat_id),
            'message_id': int(message_id),
            'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nThat slot was already taken! Sorry, no available slots at the moment."
        }
        response = requests.post(edit_url, json=payload)

def collapse_unused_slots(chat_id):
    item = table.get_item(
                Key={'id': str(chat_id)}
            )
    item = item.get('Item')
    old_message_id = item["message_id"]
    payload = {
        'chat_id': str(chat_id),
        'message_id': int(old_message_id),
        'text': "Hello! Let's schedule an appointment. Please choose one of the available slots:\n\nYou didn't pick a slot.",
    }
    response = requests.post(edit_url, json=payload)
     
def ask_to_cancel_appointment(chat_id, appointment_id):
    item = table.get_item(
        Key={'id': appointment_id}
    )
    item = item.get('Item')
    appointment_times = item["appointment_times"]
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
    response_dict = response.json()
    sent_message_id = response_dict['result']['message_id']
    table.update_item(
    Key={
        'id': str(chat_id),
        },
        UpdateExpression="SET canceling_options_message_id = :canceling_options_message_id",
        ExpressionAttributeValues={':canceling_options_message_id': str(sent_message_id)}
    )
        
def schedule_appointment(chat_id, appointment_id, message_id): 
    # get the chosen slot
    item = table.get_item(
        Key={'id': str(appointment_id)}
    )
    item = item.get('Item')
    if item.get("is_available"): # also captures the check of expired adtes, asin in that case it is None
        appointment_times = item.get("appointment_times")
        response_text = f"You selected: {item['appointment_times']}."
        new_message_text = f"Hello! Let's schedule an appointment. Please choose one of the available slots:\n\n{response_text}"
        
        payload = {
            'chat_id': str(chat_id),
            'message_id': int(message_id),
            'text': new_message_text
        }
        response = requests.post(edit_url, json=payload)

        payload = {
            'chat_id': str(chat_id),
            'text': f"An appointment at {item['appointment_times']} was successfully scheduled for you. See you soon!"
        }
        response = requests.post(sendMessage_url, json=payload) 

        chat_item = table.get_item(
            Key={'id': str(chat_id)}
        )
        chat_item = chat_item.get('Item')

        table.update_item(
            Key={
                'id': appointment_id,
            },
            UpdateExpression="SET is_available = :false, chat_id = :chat_id, username = :username, full_name = :full_name",
            ExpressionAttributeValues={
                ':false': False,
                ':chat_id': str(chat_id),
                ':username': chat_item['username'],
                ':full_name': chat_item['full_name']
            }
        )
        table.update_item(
            Key={
                'id': str(chat_id),
            },
            UpdateExpression="SET appointment_id = :appointment_id, appointment_times = :appointment_times, message_id = :none",
            ExpressionAttributeValues={
                ':appointment_id': appointment_id,
                ':appointment_times': appointment_times,
                ':none': None
            }
        )
        edit_open_suggestions()
    else:
        send_available_slots_again(chat_id, message_id)

def too_late_to_cancel_appointment(chat_id, appointment_times):
    payload = {
        'chat_id': str(chat_id),
        'text': f"It is too late to cancel or reschedule your appointment. Your appointment remains at {appointment_times}. See you soon!",
    }
    response = requests.post(sendMessage_url, json=payload)        

def show_data_to_admin(chat_id):
    response = table.scan(
        FilterExpression=Attr('chat_id').exists() & Attr('chat_id').ne(None)
    )
    scheduled_slots = response.get('Items', [])
    
    if scheduled_slots:
        sorted_scheduled_slots = sorted(scheduled_slots, key=lambda x: x['appointment_times'])
        calendar_summary = "Calendar:"
        for index, scheduled_slot in enumerate(sorted_scheduled_slots):
            calendar_summary += f"\n\n{index + 1}.\nAppointment times: {scheduled_slot['appointment_times']}\nUsername: {scheduled_slot['username']}\nFull name: {scheduled_slot['full_name']}"
    else:
         calendar_summary = "No scheduled appointments."       

    payload = {
        'chat_id': str(chat_id),
        'text': calendar_summary,
    }
    response = requests.post(sendMessage_url, json=payload)     

def edit_open_suggestions():
    response = table.scan(
        FilterExpression=Attr('message_id').exists() & Attr('message_id').ne(None)
    )
    items = response.get('Items', [])

    for item in items:
        available_slots = fetch_available_slots()
        if available_slots:
            keyboard = [[{"text": slot['appointment_times'], "callback_data": slot['id']}] for slot in available_slots]
            text = "Hello! Let's schedule an appointment. Please choose one of the available slots:"   
            payload = {
                'chat_id': str(item['chat_id']),
                'message_id': int(item['message_id']),
                'text': text,
                'reply_markup': {"inline_keyboard": keyboard}
            }
            response = requests.post(edit_url, json=payload)

