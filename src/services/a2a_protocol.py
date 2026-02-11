"""
A2Aプロトコル実装

Agent-to-Agent通信プロトコルの実装
"""

import asyncio
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from collections import deque

from ..models.a2a_message import A2AMessage, MessageType, MessageStatus


class A2AProtocol:
    """
    Agent-to-Agent通信プロトコル

    エージェント間のメッセージ交換を管理するプロトコル実装

    Attributes:
        agent_name: このプロトコルを使用するエージェント名
        message_queue: メッセージキュー
        handlers: メッセージハンドラーの辞書
        timeout: デフォルトのタイムアウト時間（秒）
    """

    def __init__(self, agent_name: str, timeout: float = 180.0):
        """
        A2Aプロトコルの初期化

        Args:
            agent_name: エージェント名
            timeout: デフォルトのタイムアウト時間（秒）
        """
        self.agent_name = agent_name
        self.timeout = timeout
        self.message_queue: deque = deque()
        self.handlers: Dict[str, Callable] = {}
        self.sent_messages: Dict[str, A2AMessage] = {}
        self.received_messages: Dict[str, A2AMessage] = {}

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[A2AMessage], Any]
    ) -> None:
        """
        メッセージタイプに対するハンドラーを登録

        Args:
            message_type: メッセージタイプ
            handler: ハンドラー関数
        """
        self.handlers[message_type.value] = handler

    async def send_message(
        self,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> A2AMessage:
        """
        メッセージを送信

        Args:
            receiver: 受信者のエージェント名
            message_type: メッセージタイプ
            content: メッセージ内容
            metadata: 追加のメタデータ

        Returns:
            送信されたメッセージ
        """
        message = A2AMessage(
            sender=self.agent_name,
            receiver=receiver,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )

        message.status = MessageStatus.SENT
        self.sent_messages[message.message_id] = message

        return message

    async def receive_message(
        self,
        message: A2AMessage,
        timeout: Optional[float] = None
    ) -> Optional[A2AMessage]:
        """
        メッセージを受信して処理

        Args:
            message: 受信したメッセージ
            timeout: タイムアウト時間（秒）

        Returns:
            処理結果のメッセージ（ある場合）
        """
        if message.receiver != self.agent_name:
            raise ValueError(
                f"メッセージの受信者が一致しません: "
                f"期待={self.agent_name}, 実際={message.receiver}"
            )

        message.status = MessageStatus.RECEIVED
        self.received_messages[message.message_id] = message

        # ハンドラーがあれば実行
        handler = self.handlers.get(message.message_type.value)
        if handler:
            try:
                if timeout is None:
                    timeout = self.timeout

                # タイムアウト付きでハンドラーを実行
                response = await asyncio.wait_for(
                    handler(message),
                    timeout=timeout
                )

                message.status = MessageStatus.PROCESSED

                # レスポンスがある場合はメッセージとして返す
                if response:
                    return await self.send_message(
                        receiver=message.sender,
                        message_type=MessageType.RESPONSE,
                        content=response,
                        metadata={"request_id": message.message_id}
                    )

            except asyncio.TimeoutError:
                message.status = MessageStatus.FAILED
                return await self.send_message(
                    receiver=message.sender,
                    message_type=MessageType.TIMEOUT,
                    content={"error": "タイムアウト"},
                    metadata={"request_id": message.message_id}
                )
            except Exception as e:
                message.status = MessageStatus.FAILED
                return await self.send_message(
                    receiver=message.sender,
                    message_type=MessageType.ERROR,
                    content={"error": str(e)},
                    metadata={"request_id": message.message_id}
                )

        return None

    def get_message_history(self) -> Dict[str, Any]:
        """
        メッセージ履歴を取得

        Returns:
            送受信メッセージの履歴
        """
        return {
            "sent": [msg.to_dict() for msg in self.sent_messages.values()],
            "received": [msg.to_dict() for msg in self.received_messages.values()]
        }

    def clear_history(self) -> None:
        """メッセージ履歴をクリア"""
        self.sent_messages.clear()
        self.received_messages.clear()

    def __repr__(self) -> str:
        """プロトコルの文字列表現"""
        return (
            f"A2AProtocol(agent={self.agent_name}, "
            f"timeout={self.timeout}s, "
            f"sent={len(self.sent_messages)}, "
            f"received={len(self.received_messages)})"
        )
