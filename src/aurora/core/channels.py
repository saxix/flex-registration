import json

from channels.generic.websocket import WebsocketConsumer
from django.urls import re_path


class FieldEditorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))


websocket_urlpatterns = [
    re_path(r"editor/field/(?P<channel>\w+)/$", FieldEditorConsumer.as_asgi()),
]
