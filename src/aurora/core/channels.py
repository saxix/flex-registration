import json
from urllib import parse

from channels.generic.websocket import WebsocketConsumer
from django.urls import path


class FieldEditorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        data = dict(parse.parse_qsl(text_data))
        for i in ["/widget/field/297/", "297"]:
            print("src/aurora/core/channels.py: 111111", i)
            self.channel_layer.send(i, {"message": data})
        # self.send(text_data=json.dumps({"message": data}))


class FieldWidgetConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        data = parse.parse_qs(text_data)
        self.send(text_data=json.dumps({"message": data}))


websocket_urlpatterns = [
    path("editor/field/<int:field>/", FieldEditorConsumer.as_asgi()),
    path("widget/field/<int:field>/", FieldWidgetConsumer.as_asgi()),
]
