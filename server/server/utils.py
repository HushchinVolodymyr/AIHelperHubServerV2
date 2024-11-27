import os

import requests
from rest_framework import status
from rest_framework.response import Response

def captcha_v2_verify(captcha_token):
    # Get reCaptcha key
    CAPTCHA_SECRET = os.getenv('CAPTCHA_V2_KEY')

    # Payload for request
    payload = {
        "secret": CAPTCHA_SECRET,
        "response": captcha_token,
    }

    # Verify token
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = response.json()

    if result.get('success'):
        return True
    else:
        return False

def captcha_v3_verify(captcha_token):
    # Get reCaptcha key
    CAPTCHA_SECRET = os.getenv('CAPTCHA_V3_KEY')

    # Verify token
    google_url_with_data = f"https://www.google.com/recaptcha/api/siteverify?secret={CAPTCHA_SECRET}&response={captcha_token}"

    response = requests.post(google_url_with_data).json()

    if response['success']:
        if response['score'] >= 0.8:
            return True

    return False

def bad_request(message: str):
    return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

def ok_request(message: str):
    return Response({"message": message}, status=status.HTTP_200_OK)