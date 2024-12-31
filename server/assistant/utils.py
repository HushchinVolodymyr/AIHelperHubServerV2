import time
import re
from datetime import datetime

from openai import OpenAI
import json

from assistant.models import Message


class AssistantUtil:
    def __init__(self, api_key: str, message: str, assistant: list) -> None:
        self.API_KEY = api_key
        self.message = message
        self.assistant = assistant
        self.assistant_id = str(assistant['assistant_id'])
        self.client = OpenAI(api_key=self.API_KEY)

    def __clean_meta_info(self, text: str) -> str:
        return re.sub(r'【\d+:\d+†source】', '', text)

    def generate_response(self) -> str:
        run_object = self.client.beta.threads.create_and_run(
            assistant_id=self.assistant_id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": self.message["message"]
                    },
                    {
                        "role": "assistant",
                        "content": "Provide response confidence in the range of 0.0-1.0. It`s necessary if cant` write 0.0! At the end if message in pattern Confidence score:  0.0"
                    }
                ],

            }
        )

        run_result = json.loads(run_object.json())

        run_id = run_result['id']
        thread_id = run_result['thread_id']

        run_status = run_object.status

        while run_status not in ["completed", "cancelled", "expired", "failed"]:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id).status
            print(f"Run status: {run_status}")
            time.sleep(2)


        thread_messages = self.client.beta.threads.messages.list(thread_id=thread_id)

        data = json.loads(thread_messages.data[0].json())



        message_response = data['content'][0]['text']['value']

        match = re.search(r"Confidence score: (\d+\.\d+)", message_response)

        confidence_score = None
        message = message_response

        if match:
            confidence_score = float(match.group(1))
            message = re.sub(r"Confidence score: \d+\.\d+", "", message_response).strip()

        cleaned_response = self.__clean_meta_info(message)

        # Message.objects.create(
        #     request_message=self.message['message'],
        #     response_message=data['content'][0]['text']['value'],
        #     confidence_score= confidence_score,
        #     data=str(datetime.now()),
        # )

        return cleaned_response, confidence_score
