from botocore.exceptions import ClientError

def refresh_access_token(client, refresh_token, client_id):
    try:
        response = client.admin_initiate_auth(
            UserPoolId='eu-west-1_BZy97DfFY',
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        new_access_token = response['AuthenticationResult']['AccessToken']
        new_id_token = response['AuthenticationResult']['IdToken']
        # Extract username or other details as needed
        user_info = client.get_user(AccessToken=new_access_token)
        username = user_info['Username']

        return {
            'AccessToken': new_access_token,
            'IdToken': new_id_token,
            'Username': username
        }

    except ClientError as e:
        raise e  # Re-raise the exception to handle it in the calling function