from django.db import models

from users.models import User

# Create your models here.
class Assistant(models.Model):
    name = models.CharField(max_length=100, nullable=False)
    description = models.TextField()
    assistant_id = models.CharField(max_length=255, nullable=False)
    user = models.ForeignKey(User, related_name="assistants", on_delete=models.CASCADE, nullable=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    assistant = models.ForeignKey(Assistant, related_name="messages", on_delete=models.CASCADE)
    request_message = models.TextField()
    response_message = models.TextField()
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.id} for Assistant {self.assistant}"