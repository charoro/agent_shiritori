"""
外部サービス連携モジュール

Google ADKなどの外部サービスとの連携機能を提供します。
"""

from .google_adk import GoogleADKService
from .a2a_protocol import A2AProtocol

__all__ = ["GoogleADKService", "A2AProtocol"]
