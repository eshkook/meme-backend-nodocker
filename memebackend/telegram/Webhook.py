# TOKEN: Final = "6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg"

# the api gateway: (attatch it to 'url' key to the setWebhook post, in body->form data)
# "https://xk8r88ywm0.execute-api.eu-west-1.amazonaws.com/botox_function"

# To Steup Webhook for Telegram Bot: (make this post requestto let telgram know where to send the messages)
# f"https://api.telegram.org/bot{TOKEN}/setWebhook"
# f"https://api.telegram.org/bot6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg/setWebhook"

import json
import requests

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = None
        text = None
        query_data = None
        
        if 'message' in body:
            chat_id = body['message']['chat']['id']
            text = body['message'].get('text', '')
        elif 'callback_query' in body:
            chat_id = body['callback_query']['message']['chat']['id']
            query_data = body['callback_query']['data']  # This will be 'bored', 'afraid', or 'bad'
        
        url = f'https://api.telegram.org/bot6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg/sendMessage'

        if text:
            if text.lower() == '/start':
                payload = {
                    'chat_id': chat_id,
                    'text': 'Hello! Keep your mouth shut and fast'
                }
                response = requests.post(url, json=payload)
            elif text.lower() == '/help':
                payload = {
                    'chat_id': chat_id,
                    'text': 'What is so hard???'
                }
                response = requests.post(url, json=payload)
            elif text.lower() == '/custom':
                payload = {
                    'chat_id': chat_id,
                    'text': 'It is a custom command. Quiet'
                }
                response = requests.post(url, json=payload)
            else:
                words_amount = len(text.split())
                if words_amount < 5:
                    response_text = f"You wrote {words_amount} words"
                    payload = {
                        'chat_id': chat_id,
                        'text': response_text
                    }
                    response = requests.post(url, json=payload)
                else:
                    keyboard = [
                        [{"text": "because I am bored", "callback_data": 'bored'}],
                        [{"text": "because I am afraid", "callback_data": 'afraid'}],
                        [{"text": "because I am bad", "callback_data": 'bad'}]
                    ]
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Why do you speak too much?',
                        'reply_markup': {"inline_keyboard": keyboard}
                    }
                    response = requests.post(url, json=payload)
        elif query_data:
            responses = {
                'bored': "Bored? It sounds like you need some excitement in your life.",
                'afraid': "Afraid? Don't worry, I'm here to help!",
                'bad': "Bad? Oh no! Hopefully, things will turn around soon."
            }
            response_text = responses.get(query_data, "Invalid choice")
            selected_option_text = {
                'bored': "You selected: because I am bored",
                'afraid': "You selected: because I am afraid",
                'bad': "You selected: because I am bad"
            }
            new_message_text = f'Why do you speak too much?\n{selected_option_text.get(query_data, "Invalid choice")}'
            # First, send the predefined response
            payload = {
                'chat_id': chat_id,
                'text': response_text
            }
            response = requests.post(url, json=payload)
            # Then, edit the original message text
            edit_url = f'https://api.telegram.org/bot6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg/editMessageText'
            payload = {
                'chat_id': chat_id,
                'message_id': body['callback_query']['message']['message_id'],
                'text': new_message_text
            }
            response = requests.post(edit_url, json=payload)

        return {
            "statusCode": 200
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "statusCode": 200
        }



# import json
# import requests

# def lambda_handler(event, context):
#     print(event)
#     try:
#         body=json.loads(event['body'])
        
#         print(body)
        
        
#         message_part=body['message'].get('text')
#         print("Message part : {}".format(message_part))
        
#         data = {'url': message_part}
        
#         payload=requests.post('https://cleanuri.com/api/v1/shorten',...)
#         short_url=payload.json()['result_url']
#         print("The short url is : {}".format(short_url))
        
#         chat_id=body['message']['chat']['id']
        
#         # url = f'https://api.telegram.org/bot{HTTP Token}/sendMessage' #############
#         url = f'https://api.telegram.org/bot6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg/sendMessage' #################
#         payload = {
#                     'chat_id': chat_id,
#                     'text': short_url
#                     }
       
#         r = requests.post(url,json=payload)
        
#         return  {
#             "statusCode": 200
#         }
#     except:
#         return  {
#         "statusCode": 200
#     }