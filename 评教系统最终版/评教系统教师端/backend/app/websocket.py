from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List, Optional
import json

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃的WebSocket连接，格式：{user_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储用户订阅的频道，格式：{user_id: [channel1, channel2, ...]}
        self.user_subscriptions: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = []
        print(f"User {user_id} connected")
    
    def disconnect(self, user_id: str):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """发送个人消息"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict, channel: Optional[str] = None):
        """广播消息到指定频道或所有用户"""
        for user_id, websocket in self.active_connections.items():
            # 如果指定了频道，只发送给订阅了该频道的用户
            if channel:
                if user_id in self.user_subscriptions and channel in self.user_subscriptions[user_id]:
                    await websocket.send_json(message)
            else:
                # 否则发送给所有用户
                await websocket.send_json(message)
    
    def subscribe(self, user_id: str, channel: str):
        """用户订阅频道"""
        if user_id in self.user_subscriptions:
            if channel not in self.user_subscriptions[user_id]:
                self.user_subscriptions[user_id].append(channel)
                print(f"User {user_id} subscribed to channel {channel}")
    
    def unsubscribe(self, user_id: str, channel: str):
        """用户取消订阅频道"""
        if user_id in self.user_subscriptions and channel in self.user_subscriptions[user_id]:
            self.user_subscriptions[user_id].remove(channel)
            print(f"User {user_id} unsubscribed from channel {channel}")


# 创建全局连接管理器实例
manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket端点"""
    # 接受连接
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            if message.get("type") == "subscribe":
                # 订阅频道
                channel = message.get("channel")
                if channel:
                    manager.subscribe(user_id, channel)
            elif message.get("type") == "unsubscribe":
                # 取消订阅频道
                channel = message.get("channel")
                if channel:
                    manager.unsubscribe(user_id, channel)
            elif message.get("type") == "message":
                # 发送消息
                content = message.get("content")
                target_user = message.get("target")
                if target_user:
                    # 发送个人消息
                    await manager.send_personal_message({"content": content}, target_user)
                else:
                    # 广播消息
                    await manager.broadcast({"content": content})
    except WebSocketDisconnect:
        # 断开连接
        manager.disconnect(user_id)


async def send_notification(user_id: str, title: str, message: str):
    """发送通知"""
    notification = {
        "type": "notification",
        "title": title,
        "message": message,
        "timestamp": "2024-01-01T00:00:00Z"  # 实际项目中应该使用当前时间
    }
    await manager.send_personal_message(notification, user_id)


async def broadcast_evaluation_update(course_id: str, evaluation_data: dict):
    """广播评估更新"""
    message = {
        "type": "evaluation_update",
        "course_id": course_id,
        "data": evaluation_data
    }
    await manager.broadcast(message, channel=f"course_{course_id}")
