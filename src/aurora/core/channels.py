import json

from channels.generic.websocket import WebsocketConsumer
from django.urls import path


class FieldEditorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        print("src/aurora/core/channels.py: 15", 8888888, text_data, bytes_data)
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        message = "aaaaaa"
        self.send(text_data=json.dumps({"message": message}))


websocket_urlpatterns = [
    path("editor/field/<int:field>/", FieldEditorConsumer.as_asgi()),
]
