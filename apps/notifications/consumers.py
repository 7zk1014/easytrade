from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SellerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.seller_id = self.scope['url_route']['kwargs']['seller_id']
        await self.channel_layer.group_add(
            f'seller_{self.seller_id}',
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        pass

    async def seller_notification(self, event):
        await self.send(text_data=json.dumps(event['message']))