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
        message_text = body['message'].get('text')
        chat_id = body['message']['chat']['id']

        # Define the Telegram Bot API URL
        url = f'https://api.telegram.org/bot6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg/sendMessage'

        # Check if the message is the start command or a regular message
        if message_text == '/start':
            # Respond with a welcome message
            payload = {
                'chat_id': chat_id,
                'text': 'Hello! How can I help you?'
            }
        else:
            # Count the number of words in the message
            word_count = len(message_text.split())
            # Determine the response based on the word count
            if word_count < 5:
                response_text = f'You wrote {word_count} words'
            else:
                response_text = 'You talk too much'
            
            # Create the payload with the determined response text
            payload = {
                'chat_id': chat_id,
                'text': response_text
            }

        # Send the response message
        response = requests.post(url, json=payload)
        
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