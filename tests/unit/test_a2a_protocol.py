"""
A2Aプロトコルのユニットテスト

A2AProtocolクラスの主要な機能をテストします。
"""

import pytest
from unittest.mock import AsyncMock
from src.services.a2a_protocol import A2AProtocol
from src.models.a2a_message import A2AMessage, MessageType, MessageStatus


class TestA2AProtocol:
    """A2Aプロトコルのテストクラス"""

    def test_protocol_initialization(self):
        """プロトコルの初期化テスト"""
        protocol = A2AProtocol(agent_name="テストエージェント", timeout=5.0)

        assert protocol.agent_name == "テストエージェント"
        assert protocol.timeout == 5.0
        assert len(protocol.handlers) == 0
        assert len(protocol.sent_messages) == 0
        assert len(protocol.received_messages) == 0

    def test_register_handler(self):
        """ハンドラー登録テスト"""
        protocol = A2AProtocol(agent_name="テスト")

        async def test_handler(message):
            return {"result": "ok"}

        # ハンドラーを登録
        protocol.register_handler(MessageType.REQUEST, test_handler)

        assert MessageType.REQUEST.value in protocol.handlers
        assert protocol.handlers[MessageType.REQUEST.value] == test_handler

    @pytest.mark.asyncio
    async def test_send_message(self):
        """メッセージ送信テスト"""
        protocol = A2AProtocol(agent_name="送信者")

        message = await protocol.send_message(
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )

        assert message.sender == "送信者"
        assert message.receiver == "受信者"
        assert message.message_type == MessageType.REQUEST
        assert message.content["data"] == "test"
        assert message.status == MessageStatus.SENT
        assert message.message_id in protocol.sent_messages

    @pytest.mark.asyncio
    async def test_receive_message_with_handler(self):
        """ハンドラー付きメッセージ受信テスト"""
        protocol = A2AProtocol(agent_name="受信者")

        # ハンドラーを登録
        async def test_handler(message):
            return {"response": "処理完了"}

        protocol.register_handler(MessageType.REQUEST, test_handler)

        # メッセージを作成
        message = A2AMessage(
            sender="送信者",
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )

        # メッセージを受信
        response = await protocol.receive_message(message)

        assert message.status == MessageStatus.PROCESSED
        assert message.message_id in protocol.received_messages
        assert response is not None
        assert response.content["response"] == "処理完了"

    @pytest.mark.asyncio
    async def test_receive_message_timeout(self):
        """メッセージ受信タイムアウトテスト"""
        protocol = A2AProtocol(agent_name="受信者", timeout=0.1)

        # 遅いハンドラーを登録
        async def slow_handler(message):
            import asyncio
            await asyncio.sleep(1.0)  # 1秒待機（タイムアウトより長い）
            return {"response": "完了"}

        protocol.register_handler(MessageType.REQUEST, slow_handler)

        # メッセージを作成
        message = A2AMessage(
            sender="送信者",
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )

        # メッセージを受信（タイムアウトする）
        response = await protocol.receive_message(message, timeout=0.1)

        assert message.status == MessageStatus.FAILED
        assert response is not None
        assert response.message_type == MessageType.TIMEOUT

    @pytest.mark.asyncio
    async def test_receive_message_error(self):
        """メッセージ受信エラーテスト"""
        protocol = A2AProtocol(agent_name="受信者")

        # エラーを発生させるハンドラー
        async def error_handler(message):
            raise ValueError("テストエラー")

        protocol.register_handler(MessageType.REQUEST, error_handler)

        # メッセージを作成
        message = A2AMessage(
            sender="送信者",
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )

        # メッセージを受信（エラーが発生）
        response = await protocol.receive_message(message)

        assert message.status == MessageStatus.FAILED
        assert response is not None
        assert response.message_type == MessageType.ERROR
        assert "テストエラー" in response.content["error"]

    @pytest.mark.asyncio
    async def test_receive_message_wrong_receiver(self):
        """間違った受信者へのメッセージテスト"""
        protocol = A2AProtocol(agent_name="正しい受信者")

        # 間違った受信者のメッセージ
        message = A2AMessage(
            sender="送信者",
            receiver="間違った受信者",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )

        # ValueErrorが発生することを確認
        with pytest.raises(ValueError) as exc_info:
            await protocol.receive_message(message)

        assert "受信者が一致しません" in str(exc_info.value)

    def test_get_message_history(self):
        """メッセージ履歴取得テスト"""
        protocol = A2AProtocol(agent_name="テスト")

        # 送信メッセージを追加
        sent_msg = A2AMessage(
            sender="テスト",
            receiver="相手",
            message_type=MessageType.REQUEST,
            content={"data": "sent"}
        )
        protocol.sent_messages[sent_msg.message_id] = sent_msg

        # 受信メッセージを追加
        recv_msg = A2AMessage(
            sender="相手",
            receiver="テスト",
            message_type=MessageType.RESPONSE,
            content={"data": "received"}
        )
        protocol.received_messages[recv_msg.message_id] = recv_msg

        # 履歴を取得
        history = protocol.get_message_history()

        assert len(history["sent"]) == 1
        assert len(history["received"]) == 1
        assert history["sent"][0]["content"]["data"] == "sent"
        assert history["received"][0]["content"]["data"] == "received"

    def test_clear_history(self):
        """履歴クリアテスト"""
        protocol = A2AProtocol(agent_name="テスト")

        # メッセージを追加
        msg = A2AMessage(
            sender="テスト",
            receiver="相手",
            message_type=MessageType.REQUEST,
            content={"data": "test"}
        )
        protocol.sent_messages[msg.message_id] = msg

        # 履歴をクリア
        protocol.clear_history()

        assert len(protocol.sent_messages) == 0
        assert len(protocol.received_messages) == 0


class TestA2AMessage:
    """A2Aメッセージのテストクラス"""

    def test_message_creation(self):
        """メッセージ作成テスト"""
        message = A2AMessage(
            sender="送信者",
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"test": "data"}
        )

        assert message.sender == "送信者"
        assert message.receiver == "受信者"
        assert message.message_type == MessageType.REQUEST
        assert message.content["test"] == "data"
        assert message.status == MessageStatus.PENDING

    def test_message_to_dict(self):
        """メッセージの辞書変換テスト"""
        message = A2AMessage(
            sender="送信者",
            receiver="受信者",
            message_type=MessageType.REQUEST,
            content={"test": "data"},
            metadata={"key": "value"}
        )

        message_dict = message.to_dict()

        assert message_dict["sender"] == "送信者"
        assert message_dict["receiver"] == "受信者"
        assert message_dict["message_type"] == "request"
        assert message_dict["content"]["test"] == "data"
        assert message_dict["metadata"]["key"] == "value"
        assert message_dict["status"] == "pending"

    def test_message_from_dict(self):
        """辞書からメッセージ作成テスト"""
        data = {
            "message_id": "123",
            "sender": "送信者",
            "receiver": "受信者",
            "message_type": "response",
            "content": {"result": "ok"},
            "metadata": {"key": "value"},
            "status": "sent"
        }

        message = A2AMessage.from_dict(data)

        assert message.message_id == "123"
        assert message.sender == "送信者"
        assert message.receiver == "受信者"
        assert message.message_type == MessageType.RESPONSE
        assert message.content["result"] == "ok"
        assert message.metadata["key"] == "value"
        assert message.status == MessageStatus.SENT
