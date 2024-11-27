import json

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from select import error

from contacts.models import Contact
from server.utils import captcha_v2_verify, bad_request, captcha_v3_verify


# Create your views here.
class ContactView(APIView):
    def post(self, request):
        request_data = json.loads(request.body)

        # Check if token present
        if request_data['token'] in "":
            return Response ({"message": "No reCaptcha token provided!"},status=status.HTTP_400_BAD_REQUEST)

        # Validate reCaptcha token by type
        if (request_data['captchaType'] == 'v2'):
            if captcha_v2_verify(request_data['token']) is False:
                return bad_request("ReCaptcha failed.")

        elif (request_data['captchaType'] == 'v3'):
            if captcha_v3_verify(request_data['token']) is False:
                return bad_request("ReCaptcha failed.")
        else:
            return bad_request("No reCaptcha type provided")

        # Create contact
        try:
            Contact.objects.create(
                name = request_data['formData']['name'],
                message = request_data['formData']['message'],
                phone = request_data['formData']['phoneNumber']
            )
            return Response({"message": "Success"}, status=status.HTTP_201_CREATED)
        except error:
            # Return bad request
            return Response({"message": "Server error!"}, status=status.HTTP_400_BAD_REQUEST)
        

