import json
import os

import requests
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response



# Create your views here.
class ContactView(APIView):
    def post(self, request):
        request_data = json.loads(request.body)

        # Check if token present
        if request_data['token'] in "":
            return Response ({"message": "No reCaptcha token provided!"},status=status.HTTP_400_BAD_REQUEST)

        # Get reCaptcha key
        CAPTCHA_V3_Key = os.getenv('CAPTCHA_V3_KEY')

        # Verify token
        google_url_with_data = f"https://www.google.com/recaptcha/api/siteverify?secret={CAPTCHA_V3_Key}&response={request_data['token']}"

        response = requests.post(google_url_with_data).json()

        if response['success']:
            if response['score'] >= 0.8:


                # Return success
                return Response({"message": "Success!"}, status=status.HTTP_200_OK)

        # Return bad request
        return Response({"message": "Invalid reCaptcha token!"}, status=status.HTTP_400_BAD_REQUEST)
        

