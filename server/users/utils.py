import requests
from server import settings

def captcha_verify(captcha_token):
    secret_re_captcha_key = settings.CAPTCHA_KEY
    payload = {
        "secret": secret_re_captcha_key,
        "response": captcha_token,
    }

    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = response.json()

    if result.get('success'):
        return True
    else:
        return False