"""
データモデルモジュール

アプリケーションで使用するデータモデルを定義します。
"""

from .a2a_message import A2AMessage, MessageType, MessageStatus

__all__ = ["A2AMessage", "MessageType", "MessageStatus"]
