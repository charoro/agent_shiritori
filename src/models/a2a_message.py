"""
A2Aプロトコルメッセージモデル

Agent-to-Agent通信のためのメッセージ構造を定義します。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """メッセージタイプの列挙型"""
    REQUEST = "request"          # リクエスト
    RESPONSE = "response"        # レスポンス
    ERROR = "error"              # エラー
    TIMEOUT = "timeout"          # タイムアウト


class MessageStatus(Enum):
    """メッセージステータスの列挙型"""
    PENDING = "pending"          # 送信待ち
    SENT = "sent"                # 送信済み
    RECEIVED = "received"        # 受信済み
    PROCESSED = "processed"      # 処理済み
    FAILED = "failed"            # 失敗


@dataclass
class A2AMessage:
    """
    A2Aプロトコルメッセージ

    エージェント間の通信に使用されるメッセージ構造

    Attributes:
        message_id: メッセージの一意なID
        sender: 送信者のエージェント名
        receiver: 受信者のエージェント名
        message_type: メッセージタイプ
        content: メッセージの内容
        metadata: 追加のメタデータ
        timestamp: メッセージ作成時刻
        status: メッセージのステータス
    """
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    message_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: MessageStatus = MessageStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """
        メッセージを辞書形式に変換

        Returns:
            メッセージの辞書表現
        """
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """
        辞書からメッセージを作成

        Args:
            data: メッセージデータの辞書

        Returns:
            A2AMessageインスタンス
        """
        return cls(
            message_id=data.get("message_id", ""),
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            status=MessageStatus(data.get("status", "pending"))
        )

    def __repr__(self) -> str:
        """メッセージの文字列表現"""
        return (
            f"A2AMessage(id={self.message_id}, "
            f"{self.sender} -> {self.receiver}, "
            f"type={self.message_type.value})"
        )
