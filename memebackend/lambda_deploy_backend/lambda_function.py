from endpoints.login import login_handler
from endpoints.signup import signup_handler
from endpoints.confirm import confirm_handler
from endpoints.authenticate import authenticate_handler
from endpoints.logout import logout_handler
from endpoints.gpt import gpt_handler
from endpoints.delete import delete_handler
from endpoints.reset_password_email_phase import reset_password_email_phase_handler
from endpoints.reset_password_code_phase import reset_password_code_phase_handler
from endpoints.cloudwatch_event import cloudwatch_event_handler

import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    action = body.get('action')

    if "source" in event and event["source"] == "aws.events":
        cloudwatch_event_handler(event)
    elif action == 'signup':
        return signup_handler(body)
    elif action == 'confirm':
        return confirm_handler(body)
    elif action == 'login':
        return login_handler(body)
    elif action == 'authenticate':
        return authenticate_handler(event)
    elif action == 'logout':
        return logout_handler(event)
    elif action == 'delete':
        return delete_handler(event)
    elif action == 'gpt':
        return gpt_handler(event)
    elif action == 'reset_password_email_phase':
        return reset_password_email_phase_handler(body)
    elif action == 'reset_password_code_phase':
        return reset_password_code_phase_handler(body)
    else:
        return {'statusCode': 400, 'body': json.dumps('Invalid action')}

#  creating a deployment package with dependencies:
# pip install timeout_decorator -t .
# pip install openai==0.28 -t .                

# then zip all files in this directory besides urllib stuff, and upload to aws lambda:

# zip in powershell with command: 
# Get-ChildItem -Path . | Where-Object { $_.Name -notlike 'function.zip' } | Compress-Archive -DestinationPath function.zip -Force

# deploy this zip to aws lambda with command: 
# aws lambda update-function-code --function-name backend_function --zip-file fileb://function.zip









