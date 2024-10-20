import time
import re

from openai import OpenAI
import json


class AssistantUtil:
    def __init__(self, api_key: str, message: str, assistant: list) -> None:
        self.API_KEY= api_key
        self.message = message
        self.assistant = assistant
        self.assistant_id = str(assistant['assistantId'])
        self.client = OpenAI(api_key=self.API_KEY)

    def __clean_meta_info(self, text: str) -> str:
        return re.sub(r'【\d+:\d+†source】', '', text)

    def generate_response(self) -> str:
        run_object = self.client.beta.threads.create_and_run(
            assistant_id=self.assistant_id,
            thread={
                "messages": [
                    {"role": "user", "content": self.message["message"]},
                ]
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

        cleaned_response = self.__clean_meta_info(message_response)

        print(cleaned_response)

        return cleaned_response