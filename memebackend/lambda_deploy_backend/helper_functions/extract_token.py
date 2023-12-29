def extract_token(cookies, token_name):
    for cookie in cookies.split(';'):
        parts = cookie.strip().split('=')
        if parts[0] == token_name and len(parts) > 1:
            return parts[1]
    return None