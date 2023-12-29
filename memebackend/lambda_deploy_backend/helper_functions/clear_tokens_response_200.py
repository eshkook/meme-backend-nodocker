import json

def clear_tokens_response_200(message):
    access_cookie = 'access_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    id_cookie = 'id_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    refresh_cookie = 'refresh_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'

    return {
            'statusCode': 200,
            'cookies': [id_cookie, access_cookie, refresh_cookie],
            'body': json.dumps(message)
        }    
