"""
Enhanced Real-Time Notification System
Created: 2025-01-09
Author: AI Assistant for QuantumVestAI
"""
import asyncio
import json
import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import aiohttp

logger = logging.getLogger("api.notifications")

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"
    MOBILE = "mobile"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationMessage:
    """Structured notification message"""
    id: str
    user_id: str
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None

class EnhancedNotificationManager:
    """Advanced notification manager with multi-channel support"""
    
    def __init__(self):
        self.subscribers = {}
        self.notification_queue = asyncio.Queue()
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",  # To be configured
            "password": "",  # To be configured
        }
        self.websocket_connections = {}
        self.mobile_tokens = {}
        self.processing_task = None
        
    async def start(self):
        """Start the notification processing task"""
        if not self.processing_task:
            self.processing_task = asyncio.create_task(self._process_notifications())
    
    async def stop(self):
        """Stop the notification processing task"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
    
    async def send_notification(self, notification: NotificationMessage):
        """Send a notification through specified channels"""
        await self.notification_queue.put(notification)
    
    async def send_price_alert(
        self,
        user_id: str,
        symbol: str,
        current_price: float,
        target_price: float,
        condition: str,
        channels: List[NotificationChannel] = None
    ):
        """Send price alert notification"""
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH]
        
        direction = "above" if condition == "greater" else "below"
        title = f"🚨 Price Alert: {symbol}"
        message = f"{symbol} is now ${current_price:.2f}, {direction} your target of ${target_price:.2f}"
        
        notification = NotificationMessage(
            id=f"price_alert_{user_id}_{symbol}_{datetime.now().timestamp()}",
            user_id=user_id,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH,
            channels=channels,
            data={
                "type": "price_alert",
                "symbol": symbol,
                "current_price": current_price,
                "target_price": target_price,
                "condition": condition
            },
            created_at=datetime.now(),
            action_url=f"/stocks/{symbol}"
        )
        
        await self.send_notification(notification)
    
    async def send_sentiment_alert(
        self,
        user_id: str,
        symbol: str,
        sentiment_score: float,
        sentiment_category: str,
        channels: List[NotificationChannel] = None
    ):
        """Send sentiment change alert"""
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH]
        
        emoji = "📈" if sentiment_score > 0 else "📉"
        title = f"{emoji} Sentiment Alert: {symbol}"
        message = f"Market sentiment for {symbol} is now {sentiment_category} (score: {sentiment_score:.2f})"
        
        notification = NotificationMessage(
            id=f"sentiment_alert_{user_id}_{symbol}_{datetime.now().timestamp()}",
            user_id=user_id,
            title=title,
            message=message,
            priority=NotificationPriority.NORMAL,
            channels=channels,
            data={
                "type": "sentiment_alert",
                "symbol": symbol,
                "sentiment_score": sentiment_score,
                "sentiment_category": sentiment_category
            },
            created_at=datetime.now(),
            action_url=f"/stocks/{symbol}/sentiment"
        )
        
        await self.send_notification(notification)
    
    async def send_ai_prediction_alert(
        self,
        user_id: str,
        symbol: str,
        prediction: Dict[str, Any],
        channels: List[NotificationChannel] = None
    ):
        """Send AI prediction alert"""
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH]
        
        confidence = prediction.get("confidence", 0)
        predicted_change = prediction.get("predicted_change", 0)
        
        emoji = "🚀" if predicted_change > 0 else "📉"
        title = f"{emoji} AI Prediction: {symbol}"
        message = f"AI predicts {symbol} will {'rise' if predicted_change > 0 else 'fall'} by {abs(predicted_change):.1f}% (confidence: {confidence:.0%})"
        
        notification = NotificationMessage(
            id=f"ai_prediction_{user_id}_{symbol}_{datetime.now().timestamp()}",
            user_id=user_id,
            title=title,
            message=message,
            priority=NotificationPriority.NORMAL,
            channels=channels,
            data={
                "type": "ai_prediction",
                "symbol": symbol,
                "prediction": prediction
            },
            created_at=datetime.now(),
            action_url=f"/stocks/{symbol}/predictions"
        )
        
        await self.send_notification(notification)
    
    async def send_portfolio_alert(
        self,
        user_id: str,
        alert_type: str,
        data: Dict[str, Any],
        channels: List[NotificationChannel] = None
    ):
        """Send portfolio-related alert"""
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH]
        
        title_map = {
            "portfolio_gain": "💰 Portfolio Milestone",
            "portfolio_loss": "⚠️ Portfolio Alert",
            "rebalance": "⚖️ Rebalancing Suggestion",
            "risk_threshold": "🔴 Risk Alert"
        }
        
        title = title_map.get(alert_type, "📊 Portfolio Update")
        message = data.get("message", "Portfolio update available")
        
        notification = NotificationMessage(
            id=f"portfolio_{alert_type}_{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            title=title,
            message=message,
            priority=NotificationPriority.NORMAL,
            channels=channels,
            data={
                "type": "portfolio_alert",
                "alert_type": alert_type,
                **data
            },
            created_at=datetime.now(),
            action_url="/portfolio"
        )
        
        await self.send_notification(notification)
    
    async def _process_notifications(self):
        """Process notifications from the queue"""
        while True:
            try:
                notification = await self.notification_queue.get()
                await self._deliver_notification(notification)
                self.notification_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
    
    async def _deliver_notification(self, notification: NotificationMessage):
        """Deliver notification through specified channels"""
        delivery_tasks = []
        
        for channel in notification.channels:
            if channel == NotificationChannel.EMAIL:
                delivery_tasks.append(self._send_email(notification))
            elif channel == NotificationChannel.SMS:
                delivery_tasks.append(self._send_sms(notification))
            elif channel == NotificationChannel.PUSH:
                delivery_tasks.append(self._send_push_notification(notification))
            elif channel == NotificationChannel.WEBSOCKET:
                delivery_tasks.append(self._send_websocket_notification(notification))
            elif channel == NotificationChannel.MOBILE:
                delivery_tasks.append(self._send_mobile_notification(notification))
        
        # Execute all delivery tasks concurrently
        results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
        
        # Log delivery results
        for i, result in enumerate(results):
            channel = notification.channels[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to deliver notification via {channel.value}: {result}")
            else:
                logger.info(f"Successfully delivered notification via {channel.value}")
    
    async def _send_email(self, notification: NotificationMessage):
        """Send email notification"""
        try:
            # Get user email from user_id (would be from database in real implementation)
            user_email = await self._get_user_email(notification.user_id)
            if not user_email:
                raise ValueError("User email not found")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config["username"]
            msg['To'] = user_email
            msg['Subject'] = notification.title
            
            # Create HTML body
            html_body = self._create_email_html(notification)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email (simulated for demo)
            # In real implementation, this would use actual SMTP
            logger.info(f"Email sent to {user_email}: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            raise
    
    async def _send_sms(self, notification: NotificationMessage):
        """Send SMS notification"""
        try:
            # Get user phone from user_id (would be from database in real implementation)
            user_phone = await self._get_user_phone(notification.user_id)
            if not user_phone:
                raise ValueError("User phone not found")
            
            # Format SMS message
            sms_message = f"{notification.title}\n{notification.message}"
            
            # Send SMS (simulated for demo)
            # In real implementation, this would use SMS service like Twilio
            logger.info(f"SMS sent to {user_phone}: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"SMS delivery failed: {e}")
            raise
    
    async def _send_push_notification(self, notification: NotificationMessage):
        """Send push notification"""
        try:
            # Get user's push tokens (would be from database in real implementation)
            push_tokens = await self._get_user_push_tokens(notification.user_id)
            if not push_tokens:
                raise ValueError("User push tokens not found")
            
            # Send push notification (simulated for demo)
            # In real implementation, this would use service like Firebase Cloud Messaging
            logger.info(f"Push notification sent to {len(push_tokens)} devices: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Push notification delivery failed: {e}")
            raise
    
    async def _send_websocket_notification(self, notification: NotificationMessage):
        """Send WebSocket notification"""
        try:
            # Get user's WebSocket connections
            connections = self.websocket_connections.get(notification.user_id, [])
            if not connections:
                raise ValueError("No active WebSocket connections")
            
            # Send to all active connections
            message = {
                "type": "notification",
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority.value,
                "data": notification.data,
                "timestamp": notification.created_at.isoformat()
            }
            
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send WebSocket message: {e}")
            
            logger.info(f"WebSocket notification sent to {len(connections)} connections")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket delivery failed: {e}")
            raise
    
    async def _send_mobile_notification(self, notification: NotificationMessage):
        """Send mobile app notification"""
        try:
            # Get user's mobile tokens
            mobile_tokens = await self._get_user_mobile_tokens(notification.user_id)
            if not mobile_tokens:
                raise ValueError("User mobile tokens not found")
            
            # Send mobile notification (simulated for demo)
            # In real implementation, this would use mobile push services
            logger.info(f"Mobile notification sent to {len(mobile_tokens)} devices: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Mobile notification delivery failed: {e}")
            raise
    
    def _create_email_html(self, notification: NotificationMessage) -> str:
        """Create HTML email body"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin: 0;">QuantumVestAI</h1>
                    <p style="color: #7f8c8d; margin: 5px 0 0 0;">AI-Powered Investment Intelligence</p>
                </div>
                
                <div style="background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #34495e; margin: 0 0 10px 0;">{notification.title}</h2>
                    <p style="color: #2c3e50; margin: 0; font-size: 16px; line-height: 1.6;">{notification.message}</p>
                </div>
                
                {f'<div style="text-align: center; margin-bottom: 20px;"><a href="{notification.action_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Details</a></div>' if notification.action_url else ''}
                
                <div style="border-top: 1px solid #bdc3c7; padding-top: 20px; margin-top: 30px;">
                    <p style="color: #7f8c8d; font-size: 12px; margin: 0; text-align: center;">
                        This notification was sent at {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from database"""
        # Simulated database lookup
        return f"user_{user_id}@example.com"
    
    async def _get_user_phone(self, user_id: str) -> Optional[str]:
        """Get user phone from database"""
        # Simulated database lookup
        return f"+1234567890"
    
    async def _get_user_push_tokens(self, user_id: str) -> List[str]:
        """Get user push tokens from database"""
        # Simulated database lookup
        return [f"push_token_{user_id}"]
    
    async def _get_user_mobile_tokens(self, user_id: str) -> List[str]:
        """Get user mobile tokens from database"""
        # Simulated database lookup
        return [f"mobile_token_{user_id}"]
    
    def register_websocket(self, user_id: str, websocket):
        """Register a WebSocket connection for a user"""
        if user_id not in self.websocket_connections:
            self.websocket_connections[user_id] = []
        self.websocket_connections[user_id].append(websocket)
    
    def unregister_websocket(self, user_id: str, websocket):
        """Unregister a WebSocket connection"""
        if user_id in self.websocket_connections:
            try:
                self.websocket_connections[user_id].remove(websocket)
                if not self.websocket_connections[user_id]:
                    del self.websocket_connections[user_id]
            except ValueError:
                pass

# Global notification manager instance
notification_manager = EnhancedNotificationManager()
