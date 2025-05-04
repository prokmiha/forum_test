from channels.generic.websocket import AsyncWebsocketConsumer
import json

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("comments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("comments", self.channel_name)

    async def receive(self, text_data):
        pass

    async def comment_created(self, event):
        await self.send(text_data=json.dumps(event["data"]))