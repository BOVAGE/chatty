from django.urls import path
from chat.views import chatroom

urlpatterns = [
    path('<str:room_name>', chatroom, name='chatroom')
]