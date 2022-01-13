from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    author = models.ForeignKey(User, related_name='message', on_delete=models.CASCADE)
    message_text = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message_text

    def last_10_messages():
        return Message.objects.order_by('-timestamp').all()[:10]