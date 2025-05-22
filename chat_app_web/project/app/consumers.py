import json
from time import localtime
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage , Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import format_timestamp
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

        messages = await self.get_last_message()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'message': msg['message'],
                'username': msg['username'],
                'timestamp': msg['timestamp'],
                'file': msg.get('file'),
                'filename': msg.get('filename')
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        username = data.get("username", "")
        file_data = data.get('file')
        file_name = data.get('file_name')

        file_obj = None
        file_url = None

        # Handle base64-encoded file data
        if file_data:
            format, imgstr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"upload_{get_random_string(8)}.{ext}"
            file_obj = ContentFile(base64.b64decode(imgstr), name=file_name)

        # Don't save if both file and message are empty
        if not message and not file_obj:
            return

        # ✅ Pass file_obj to save_message
        saved_message = await self.save_message(username, message, file_obj)

        # ✅ Check saved_message is not None before accessing .file
        file_url = saved_message.file.url if saved_message and saved_message.file else None

        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": message,
                "username": username,
                "timestamp": timezone.now().isoformat(),
                "file": file_url,
                "filename": file_name if file_url else None
            }
        )

    async def sendMessage(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "timestamp": event["timestamp"],
            "file": event.get("file"),
            "filename": event.get("filename")
        }))

    @sync_to_async
    def save_message(self, username, message, file_obj=None):
        try:
            user = User.objects.get(username=username)
            msg = ChatMessage.objects.create(
                user=user,
                message=message,
                file=file_obj
            )
            return msg  # ✅ Return saved message
        except User.DoesNotExist:
            return None  # ✅ Return None to avoid attribute errors

    @sync_to_async
    def get_last_message(self):
        user = self.scope["user"]
        if user.is_authenticated:
            joined_at = user.date_joined
            messages = ChatMessage.objects.select_related('user').filter(
                timestamp__gte=joined_at
            ).order_by('timestamp')
            return [
                {
                    "username": msg.user.username,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "file": msg.file.url if msg.file else None,
                    "filename": msg.file.name.split("/")[-1] if msg.file else None
                }
                for msg in messages
            ]
        return []






import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.exceptions import PermissionDenied as DenyConnection
from .models import Message  # Make sure you import your Message model
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['user']
        
        # Prevent anonymous users from connecting
        if not self.sender.is_authenticated:
            raise DenyConnection("User is not authenticated.")

        # Get receiver user from URL
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']
        try:
            self.receiver = await database_sync_to_async(User.objects.get)(id=self.receiver_id)
        except User.DoesNotExist:
            await self.close()
            return

        # Generate a unique room name for the private chat
        self.room_name = f"chat_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        # Send the latest 50 messages to the user
        messages = await self.get_last_messages()
        await self.send(text_data=json.dumps({
            "type": "last_messages",
            "messages": messages
        }))

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        file_data = data.get('file')
        file_name = data.get('file_name')

        file_obj = None
        file_url = None

        # Handle base64-encoded file data
        if file_data:
            format, imgstr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"upload_{get_random_string(8)}.{ext}"
            file_obj = ContentFile(base64.b64decode(imgstr), name=file_name)
            
        if not message and not file_obj:
            return  # Ignore empty messages

        # Save the message to the database and get back the instance
        saved_message = await self.save_message(self.sender, self.receiver, message, file_obj)

        # Get file URL from the saved message
        file_url = saved_message.file.url if saved_message.file else None

        # Send the message to the group
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "message": message,
                "sender": self.sender.username,
                "sender_id": self.sender.id,
                "timestamp": saved_message.timestamp.isoformat(),
                "file": file_url,
                "filename": file_name if file_url else None
            }
        )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
            "file": event.get("file"),
            "filename": event.get("filename")
        }))

    @database_sync_to_async
    def get_last_messages(self):
        try:
            messages = list(
                Message.objects.filter(
                    sender__in=[self.sender, self.receiver],
                    receiver__in=[self.sender, self.receiver]
                ).order_by('-timestamp')[:50]
            )[::-1]

            return [
                {
                    "sender": msg.sender.username,
                    "sender_id": msg.sender.id,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "file": msg.file.url if msg.file else None,
                    "filename": msg.file.name.split("/")[-1] if msg.file else None
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []

    @database_sync_to_async
    def save_message(self, sender, receiver, message, file_obj=None):
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            file=file_obj
        )
