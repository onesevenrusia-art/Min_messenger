import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from channels.layers import get_channel_layer


from .models import MessageModel
from accounts.models import DepositsModel, Profile, ManagerChannel
from accounts.utils import send_message, send_message_with_markup
from technical.models import BotsConfiguration

class PracticeConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data == 'PING':
            await self.send('PONG')

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': event['message'],
            'message_id': event['message_id'],
            'deposit_id': event['deposit_id'],
            'time': event['time']
        }))


class MessageConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """ Connects the WebSocket client based on the user ID. """
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        
        safe_user_id = str(self.user_id).strip()
        
        if len(safe_user_id) > 50:
            await self.close()
            return

        self.group_name = f"user_{safe_user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        

    async def disconnect(self, close_code):
        """ Disconnects the WebSocket client. """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """ Processes incoming messages and broadcasts them. """
        if str(text_data).startswith("create"):
            deposit_id, message_content, __from = str(text_data).split(":")[1:4]

            deposit = await self.get_deposit(deposit_id)
            if deposit:
                if __from == "client":
                    status = "success"
                    sender = await self.get_manager(deposit_id)
                    creator_profile = deposit.creator_id
                    sells_bot = await self.get_sells_bot()
                    chat_id = None  

                    if creator_profile and creator_profile.telegram_id:
                        message_text = f'[#T{deposit.id}] Получено новое сообщение по платежу\n\n{message_content}\n\nОтветьте на него, воспользовавшись кнопкой ниже'
                        chat_id = creator_profile.telegram_id
                    
                elif __from == "bot":
                    status = "notification"
                    sender = deposit.creator_id

                message_json = await self.create_message(deposit, message_content, sender)

                manager = await self.get_manager(deposit_id)
                await self.channel_layer.group_send(
                        f"user_{manager.telegram_id}",
                        {
                            "type": "chat_message",
                            "status": status,
                            "message": message_content,
                            "message_id": message_json["pk"],
                            "deposit_id": message_json["fields"]["deposit"],
                            "time": message_json["fields"]["created_at"],
                            "source": "message"
                        },
                    )

                if status == "success" and sells_bot and chat_id:
                    markup = {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Ответить",
                                    "callback_data": f'deposits:chat:m:{message_json["pk"]}'
                                },
                            ]
                        ]
                    }
send_message_with_markup(sells_bot, chat_id, message_text, markup)

            else:
                await self.send(text_data=json.dumps({
                    "status": "error",
                    "message": "Deposit not found."
                }))
    

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': event['message'],
            'message_id': event['message_id'],
            'deposit_id': event['deposit_id'],
            'time': event['time'],
            'source': event.get('source')
        }))

    
    @database_sync_to_async
    def get_deposit(self, deposit_id):
        try:
            return DepositsModel.objects.select_related('creator_id').get(id=deposit_id)
        except DepositsModel.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_manager(self, deposit_id):
        try:
            deposit = DepositsModel.objects.get(id=deposit_id)
            return ManagerChannel.objects.get(channel=deposit.channel).profile
        except DepositsModel.DoesNotExist:
            return None
        except ManagerChannel.DoesNotExist:
            return None

    @database_sync_to_async
    def get_sells_bot(self):
        bot_type = 'SELLS'
        try:
            return BotsConfiguration.objects.get(bot_type=bot_type).token
        except BotsConfiguration.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, deposit, content, sender):
        message = MessageModel(deposit=deposit, content=content, sender=sender)
        message.save()
        
        message_json = serialize('json', [message])
        return json.loads(message_json)[0]