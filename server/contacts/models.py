from django.db import models

# Create your models here.
class Contact(models.Model):
    __tablename__ = 'contacts'

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name