import os

from openai import OpenAI
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import json

from .utils import AssistantUtil

from .models import Assistant


# Create your views here.
class AssistantResponseView(APIView):
    def post(self, request):
        request_message = request.data['message']
        request_assistant = request.data['assistant']

        if request_assistant is None:
            return Response({"message": "Assistant not found"}, status=status.HTTP_404_NOT_FOUND)

        if request_message is None:
            return Response({"message": "No message provided"}, status=status.HTTP_404_NOT_FOUND)

        selected_assistant = None

        file_path = os.path.join(os.path.dirname(__file__), 'assistant_config.json')
        with open(file_path, 'r') as f:
            config = json.load(f)

        chat_assistants = config["AI"]["assistants"]

        for assistant_from_list in chat_assistants:
            if request_assistant["id"] == assistant_from_list["id"]:
                selected_assistant = assistant_from_list

        assistant = AssistantUtil(api_key=config["AI"]["apiKey"],
                                  message=request_message, assistant=selected_assistant)

        message = assistant.generate_response()

        response = Response(status=status.HTTP_200_OK)

        response.data = {
            "data": {
                "id": request_message["id"] + 1,
                "messageType": False,
                "message": message,
            }
        }

        return response


# Assistant CRUD View (create, update, delete, get), only authenticated user
class AssistantCRUDView(APIView):
    # Check authentication
    permission_classes = [IsAuthenticated]

    # Create assistant
    def post(self, request):
        # Get data from request
        name = request.data['name']
        instructions = request.data['instructions']
        description = request.data['description']
        temperature = request.data['temperature']
        model = request.data['model']

        # Check if data provided in request
        if model is None or temperature is None or name is None:
            return Response({"message": "No assistant create data provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get config file
        file_path = os.path.join(os.path.dirname(__file__), 'assistant_config.json')
        with open(file_path, 'r') as f:
            config = json.load(f)

        # Create OpenAI client
        open_ai_client = OpenAI(api_key=config["AI"]["apiKey"])

        # Try to create assistant
        try:
            # Create assistant via OpenAI API
            assistant = open_ai_client.beta.assistants.create(
                name=name,
                description=description,
                instructions=instructions,
                model=model,
                temperature=temperature,
                tools=[{"type": "code_interpreter"}],
            )

            # Find authenticated user
            user = request.user

            # Save assistant to database
            created_assistent = Assistant.objects.create(
                name=name,
                description=description,
                assistant_id=assistant.id,
                user=user,
            )

            # Create response
            response = Response(status=status.HTTP_201_CREATED)

            # Fill response data
            response.data = {
                "assistant": {
                    "id": created_assistent.id,
                    "name": created_assistent.name,
                    "description": created_assistent.description
                }
            }

            return response

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Get assistant
    def get(self, request, assistant_id):
        # Found assistant
        request_assistant = get_object_or_404(Assistant, pk=assistant_id, user=request.user)

        # Get config file
        file_path = os.path.join(os.path.dirname(__file__), 'assistant_config.json')
        with open(file_path, 'r') as f:
            config = json.load(f)

        # Create OpenAI client
        open_ai_client = OpenAI(api_key=config["AI"]["apiKey"])

        try:
            # Get assistant from OpenAI API
            assistant = open_ai_client.beta.assistants.retrieve(request_assistant.assistant_id)

            if assistant is None:
                return Response({"message": "Assistant not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Server error"}, status=status.HTTP_404_NOT_FOUND)

        # Create response
        response = Response(status=status.HTTP_200_OK)

        # Fill response data
        response.data = {
            "assistant": {
                "id": request_assistant.id,
                "name": assistant.name,
                "instructions": assistant.instructions,
                "description": assistant.description,
                "temperature": assistant.temperature,
                "model": assistant.model,
            }
        }

        # Return response
        return response






