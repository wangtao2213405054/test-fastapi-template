# _author: Coke
# _date: 2024/7/28 00:53
# _description: Socket IO 挂载服务

import time
from typing import Any

import socketio
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.config import settings


class UserInfo(BaseModel):
    """用户信息"""

    userId: int  # 用户ID
    connectedAt: float  # 连接到的时间
    session: str  # 用户 Session


class SocketIO(socketio.AsyncServer):
    """
    socketio 的继承类, 封装了一些方法
    """

    def __init__(self, **kwargs) -> None:  # type: ignore
        self._users: dict[int, UserInfo] = dict()
        self._session_user: dict[str, int] = dict()
        super(SocketIO, self).__init__(**kwargs)

    def __len__(self) -> int:
        """返回当前用户总数"""
        return len(self._users)

    @property
    def empty(self) -> bool:
        """检查房间是否为空"""
        return len(self._users) == 0

    @property
    def user_list(self) -> list[int]:
        """返回当前房间内的所有用户"""
        return list(self._users)

    def add_user(self, user_id: int, sid: str) -> None:
        """
        添加一个用户到房间中
        :param user_id: 用户 id
        :param sid: session id
        :return:
        """
        if user_id in self._users:
            raise ValueError("用户已经存在于房间")

        self._users[user_id] = UserInfo(userId=user_id, connectedAt=time.time(), session=sid)
        self._session_user[sid] = user_id

    async def remove_user(self, user_id: int) -> None:
        """
        从房间中移出一个用户
        :param user_id: 要移出的用户 id
        :return:
        """
        if user_id not in self._users:
            raise ValueError("用户不存在与房间中")

        user_session = self._users[user_id].session

        del self._users[user_id]
        del self._session_user[user_session]
        await self.disconnect(user_session)

    def get_user(self, user_id: int) -> UserInfo | None:
        """
        获取房间中的用户信息
        :param user_id: 用户ID
        :return:
        """
        return self._users.get(user_id)

    async def whisper(self, user_id: int, message: dict[str, Any]) -> None:
        """
        向某一用户发送消息
        :param user_id: 用户ID
        :param message: 消息体
        :return:
        """
        if user_id not in self._users:
            raise ValueError("用户不存在与房间中")

        await self.emit(jsonable_encoder(message), to=self._users[user_id].session)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        向房间内的所有用户广播一条消息
        :param message: 要广播的消息体
        :return:
        """
        if self.empty:
            raise ValueError("房间中不存在用户")

        await self.emit(jsonable_encoder(message))


socket = SocketIO(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(socket, socketio_path=settings.SOCKET_PREFIX)
