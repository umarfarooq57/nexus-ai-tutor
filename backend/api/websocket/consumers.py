"""
WebSocket consumers for real-time communication
"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class LearningSessionConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket for real-time learning session updates"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'learning_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'session_id': self.session_id
        })
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming messages"""
        message_type = content.get('type')
        
        if message_type == 'progress_update':
            await self.handle_progress_update(content)
        elif message_type == 'emotion_update':
            await self.handle_emotion_update(content)
        elif message_type == 'focus_update':
            await self.handle_focus_update(content)
    
    async def handle_progress_update(self, content):
        """Handle learning progress updates"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'progress_message',
                'progress': content.get('progress'),
                'topic': content.get('topic')
            }
        )
    
    async def handle_emotion_update(self, content):
        """Handle emotion/cognitive state updates"""
        # Store emotion data for Digital Twin
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'emotion_message',
                'emotion': content.get('emotion'),
                'cognitive_load': content.get('cognitive_load')
            }
        )
    
    async def handle_focus_update(self, content):
        """Handle focus/attention updates"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'focus_message',
                'focus_level': content.get('focus_level')
            }
        )
    
    async def progress_message(self, event):
        await self.send_json(event)
    
    async def emotion_message(self, event):
        await self.send_json(event)
    
    async def focus_message(self, event):
        await self.send_json(event)


class AIAssistantConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket for AI assistant real-time chat"""
    
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f'ai_assistant_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming AI requests"""
        message = content.get('message')
        context = content.get('context', {})
        
        # Stream AI response
        await self.send_json({
            'type': 'ai_thinking',
            'status': 'processing'
        })
        
        # Process with AI (will be implemented with actual AI service)
        response = await self.process_ai_request(message, context)
        
        await self.send_json({
            'type': 'ai_response',
            'message': response
        })
    
    async def process_ai_request(self, message, context):
        """Process AI request - placeholder for actual AI integration"""
        # This will be connected to the actual AI teaching agents
        return f"AI Response to: {message}"


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def notification_message(self, event):
        """Send notification to client"""
        await self.send_json({
            'type': 'notification',
            'notification': event['notification']
        })
