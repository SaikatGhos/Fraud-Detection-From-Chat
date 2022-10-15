
import json
from urllib import request, response
from channels.consumer import AsyncConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.contrib import messages
from django.shortcuts import redirect, render
from chat.models import ChatMessage, Thread

User = get_user_model()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print('connected',event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type':'websocket.accept'
        })

    async def websocket_receive(self,event):
        print('recevied',event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')

        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')      
        thread_id = received_data.get('thread_id')  

        if not msg:
            print("Erro: Empty message")
            return False
        # else: #i have to take the last message form here
        #     print(sent_by_id+"-is sending--"+msg+"--to--"+send_to_id)
            
        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not send_to_user:
            print('Error:: Send to user is incorrect')
        if not sent_by_user:
            print('Error:: Sent by user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')
            
        await self.create_chat_message(thread_obj, sent_by_user, msg)
        
        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']

        response = {
            'message':msg,
            'sent_by': self_user.id,
            'thread_id':thread_id
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )
        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )
        # await self.send({
        #     'type':'websocket.send',
        #     'text':json.dumps(response)
        # })

    async def sent_message(self,event):
        print('Sent_message',event)
        await self.send({
           'type':'websocket.send',
           'text':event['text']
        })


    async def websocket_disconnect(self,event):
        print('disconnected',event)

    async def chat_message(self,event):
        print('chat_message',event)
        await self.send({
            'type':'websocket.send',
            'text':event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj    



    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj  
    
    @database_sync_to_async
    def create_chat_message(self, thread,user,msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)
       