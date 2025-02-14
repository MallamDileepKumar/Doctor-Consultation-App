import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AppointmentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        self.group_name = f"appointment_{self.patient_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def appointment_update(self, event):
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "meeting_link": event["meeting_link"],
        }))
