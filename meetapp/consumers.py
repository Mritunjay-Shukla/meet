import json
from channels.generic.websocket import AsyncWebsocketConsumer

# simple memory dict {room_id: host_channel_name}
ROOM_HOSTS = {}

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        await self.channel_layer.group_add(self.room_id, self.channel_name)
        await self.accept()

        # If this client is host
        if self.scope['query_string'].decode().find("host=true") != -1:
            ROOM_HOSTS[self.room_id] = self.channel_name

        # Notify group that new user joined
        await self.channel_layer.group_send(
            self.room_id,
            {"type": "user_join", "channel": self.channel_name}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

        # remove host mapping if host disconnected
        if ROOM_HOSTS.get(self.room_id) == self.channel_name:
            del ROOM_HOSTS[self.room_id]

    async def receive(self, text_data):
        data = json.loads(text_data)

        # ---- Chat Handling ----
        if data.get("type") == "chat":
            message = data.get("message", "")

            if data.get("is_host", False):
                # Host → broadcast to everyone
                await self.channel_layer.group_send(
                    self.room_id,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": "host",
                    }
                )
            else:
                # Guest → send only to host
                host_channel = ROOM_HOSTS.get(self.room_id)
                if host_channel:
                    await self.channel_layer.send(
                        host_channel,
                        {
                            "type": "chat_message",
                            "message": message,
                            "sender": "guest",
                        }
                    )

            return

        # ---- WebRTC Signaling ----
        target = data.get("target")
        if target:
            await self.channel_layer.send(
                target,
                {"type": "signal_message", "message": data, "sender": self.channel_name}
            )
        else:
            await self.channel_layer.group_send(
                self.room_id,
                {"type": "signal_message", "message": data, "sender": self.channel_name}
            )

    # WebRTC forward
    async def signal_message(self, event):
        await self.send(text_data=json.dumps({
            **event["message"],
            "sender": event["sender"]
        }))

    # Chat forward
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "sender": event["sender"]
        }))

    # Notify host about new guest
    async def user_join(self, event):
        if event["channel"] != self.channel_name:
            await self.send(text_data=json.dumps({
                "type": "new_guest",
                "channel": event["channel"]
            }))
