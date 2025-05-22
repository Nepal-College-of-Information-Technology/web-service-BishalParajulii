from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

# Register your models here.

class ChatMessage(models.Model):
    user = models.ForeignKey(User ,  on_delete = models.CASCADE)
    message = models.TextField()
    file = models.FileField(upload_to='groupchat_files/' , blank=True , null=True)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username} : {self.message[:20]}"




class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User , on_delete = models.CASCADE , related_name='received_messages')
    message =models.TextField()
    file = models.FileField(upload_to='chat_files/' , blank=True , null=True)
    timestamp = models.DateTimeField(auto_now_add = True)
    is_read = models.BooleanField(default=False)

    @property
    def chat_id(self):
        return f"{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}"



    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.message[:20]}"

