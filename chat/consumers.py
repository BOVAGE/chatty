from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from chat.models import Message
import json

class ChatRoomConsumer(WebsocketConsumer):

    def fetch_messages(self, *data):
        messages = Message.last_10_messages()
        content = {
            'command': 'fetch_messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)


    def new_message(self, data):
        author = data['from']
        author_user = User.objects.get(username=author)
        message = Message.objects.create(author=author_user, message_text=data['message'])
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.message_text,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.fetch_messages()
        print('open...')

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard) (
            self.room_group_name,
            self.room_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.commands[text_data_json['command']](self, text_data_json)

    def send_chat_message(self, message):
        # message = text_data_json['message']
        # username = text_data_json['username']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                # 'username': username,
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chatroom_message(self, event):
        message = event['message']
        # username = event['username']

        # self.send(text_data=json.dumps({
        #     'message': message,
        #     'username': username,
        # }))
        self.send(text_data=json.dumps(message))