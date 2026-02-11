"""
しりとりエージェント実装

A2Aプロトコルを使用して日本語のしりとりを行うエージェント
"""

import asyncio
import re
from typing import Dict, Any, Optional, Set
from datetime import datetime

from .base_agent import BaseAgent
from ..services.a2a_protocol import A2AProtocol
from ..services.google_adk import GoogleADKService
from ..models.a2a_message import A2AMessage, MessageType


class ShiritoriAgent(BaseAgent):
    """
    しりとりを行うAIエージェント

    A2Aプロトコルを使用して他のエージェントとしりとりを行います。

    Attributes:
        protocol: A2Aプロトコルインスタンス
        adk_service: Google ADKサービス
        used_words: 使用済み単語のセット
        timeout: レスポンスタイムアウト（秒）
    """

    def __init__(
        self,
        name: str,
        timeout: float = 180.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        しりとりエージェントの初期化

        Args:
            name: エージェント名
            timeout: レスポンスタイムアウト（秒）
            config: 追加設定
        """
        super().__init__(name, config)
        self.protocol = A2AProtocol(agent_name=name, timeout=timeout)
        self.adk_service = GoogleADKService()
        self.used_words: Set[str] = set()
        self.timeout = timeout
        self.game_state = {
            "is_playing": False,
            "current_word": None,
            "turn_count": 0
        }

        # A2Aプロトコルのハンドラーを登録
        self.protocol.register_handler(
            MessageType.REQUEST,
            self._handle_shiritori_request
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        入力を処理

        Args:
            input_data: {
                "action": "start" | "respond",
                "word": "単語"（respondの場合）,
                "opponent": "相手のエージェント名"
            }

        Returns:
            処理結果
        """
        action = input_data.get("action")

        if action == "start":
            # ゲーム開始
            return await self._start_game(input_data)
        elif action == "respond":
            # しりとりに応答
            return await self._respond_to_word(input_data)
        else:
            return {
                "success": False,
                "error": f"不明なアクション: {action}"
            }

    async def _start_game(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ゲームを開始して最初の単語を送信

        Args:
            input_data: 入力データ

        Returns:
            最初の単語
        """
        opponent = input_data.get("opponent")
        if not opponent:
            return {"success": False, "error": "相手のエージェント名が必要です"}

        # 最初の単語を生成
        prompt = """日本語のしりとりゲームを始めます。
最初の単語を1つだけ、ひらがなで答えてください。
「ん」で終わらない、一般的な名詞を選んでください。
単語のみを答えてください。"""

        try:
            first_word = await asyncio.wait_for(
                self.adk_service.generate_text(prompt),
                timeout=self.timeout
            )

            # クリーニング：余計な文字を削除
            first_word = self._clean_word(first_word)

            # 検証
            if not self._is_valid_word(first_word):
                return {
                    "success": False,
                    "error": f"無効な単語が生成されました: {first_word}"
                }

            # 使用済み単語に追加
            self.used_words.add(first_word)
            self.game_state["current_word"] = first_word
            self.game_state["turn_count"] = 1

            # A2Aメッセージとして送信
            message = await self.protocol.send_message(
                receiver=opponent,
                message_type=MessageType.REQUEST,
                content={
                    "word": first_word,
                    "turn": 1,
                    "action": "shiritori"
                }
            )

            self.add_to_history({
                "turn": 1,
                "agent": self.name,
                "word": first_word,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "success": True,
                "word": first_word,
                "message": message.to_dict()
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "タイムアウト: 単語生成に時間がかかりすぎました"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"エラー: {str(e)}"
            }

    async def _respond_to_word(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        相手の単語に応答

        Args:
            input_data: {"word": "相手の単語", "opponent": "相手の名前"}

        Returns:
            次の単語
        """
        previous_word = input_data.get("word")
        opponent = input_data.get("opponent")

        if not previous_word or not opponent:
            return {
                "success": False,
                "error": "前の単語と相手の名前が必要です"
            }

        # 前の単語をクリーニング
        previous_word = self._clean_word(previous_word)

        # 検証
        validation_result = self._validate_previous_word(previous_word)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["reason"]
            }

        # 使用済み単語に追加
        self.used_words.add(previous_word)

        # 次の単語を生成
        last_char = previous_word[-1]

        prompt = f"""しりとりゲームの続きです。
前の単語: {previous_word}
「{last_char}」で始まる日本語の単語を1つだけ、ひらがなで答えてください。

ルール:
- 「{last_char}」で始まる単語を選んでください
- 「ん」で終わらない単語を選んでください
- 既に使われた単語は使えません: {', '.join(list(self.used_words)[-5:])}
- 一般的な名詞を選んでください
- 単語のみを答えてください"""

        try:
            next_word = await asyncio.wait_for(
                self.adk_service.generate_text(prompt),
                timeout=self.timeout
            )

            # クリーニング
            next_word = self._clean_word(next_word)

            # 検証
            if not self._is_valid_word(next_word):
                return {
                    "success": False,
                    "error": f"無効な単語が生成されました: {next_word}",
                    "is_game_over": True,
                    "winner": opponent
                }

            if next_word[0] != last_char:
                return {
                    "success": False,
                    "error": f"「{last_char}」で始まっていません: {next_word}",
                    "is_game_over": True,
                    "winner": opponent
                }

            if next_word in self.used_words:
                return {
                    "success": False,
                    "error": f"既に使われた単語です: {next_word}",
                    "is_game_over": True,
                    "winner": opponent
                }

            if next_word[-1] == 'ん':
                return {
                    "success": False,
                    "error": f"「ん」で終わってしまいました: {next_word}",
                    "is_game_over": True,
                    "winner": opponent,
                    "word": next_word
                }

            # 使用済み単語に追加
            self.used_words.add(next_word)
            self.game_state["current_word"] = next_word
            self.game_state["turn_count"] += 1

            # A2Aメッセージとして送信
            message = await self.protocol.send_message(
                receiver=opponent,
                message_type=MessageType.REQUEST,
                content={
                    "word": next_word,
                    "turn": self.game_state["turn_count"],
                    "action": "shiritori"
                }
            )

            self.add_to_history({
                "turn": self.game_state["turn_count"],
                "agent": self.name,
                "word": next_word,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "success": True,
                "word": next_word,
                "is_game_over": False,
                "message": message.to_dict()
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "タイムアウト: 応答時間切れです",
                "is_game_over": True,
                "winner": opponent
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"エラー: {str(e)}",
                "is_game_over": True,
                "winner": opponent
            }

    async def _handle_shiritori_request(
        self,
        message: A2AMessage
    ) -> Dict[str, Any]:
        """
        A2Aプロトコル経由でしりとりリクエストを処理

        Args:
            message: 受信したA2Aメッセージ

        Returns:
            応答データ
        """
        content = message.content
        word = content.get("word")

        if not word:
            return {"error": "単語が含まれていません"}

        # 応答を生成
        result = await self._respond_to_word({
            "word": word,
            "opponent": message.sender
        })

        return result

    def _clean_word(self, word: str) -> str:
        """
        単語をクリーニング

        Args:
            word: クリーニング前の単語

        Returns:
            クリーニング後の単語
        """
        # 余計な文字を削除（句読点、空白、改行など）
        word = re.sub(r'[。、！？\s\n\r「」『』（）()]', '', word)
        # 全角英数字を半角に変換してから削除
        word = word.strip()
        # ひらがなのみを抽出
        word = ''.join([c for c in word if '\u3040' <= c <= '\u309F'])
        return word.lower()

    def _is_valid_word(self, word: str) -> bool:
        """
        単語が有効かチェック

        Args:
            word: チェックする単語

        Returns:
            有効な場合True
        """
        if not word:
            return False

        # ひらがなのみで構成されているか
        if not all('\u3040' <= c <= '\u309F' for c in word):
            return False

        # 1文字以上か
        if len(word) < 1:
            return False

        return True

    def _validate_previous_word(self, word: str) -> Dict[str, Any]:
        """
        前の単語を検証

        Args:
            word: 検証する単語

        Returns:
            検証結果
        """
        if not self._is_valid_word(word):
            return {
                "valid": False,
                "reason": f"無効な単語です: {word}"
            }

        if word[-1] == 'ん':
            return {
                "valid": False,
                "reason": f"「ん」で終わっています: {word}"
            }

        return {"valid": True}

    def reset_game(self) -> None:
        """ゲーム状態をリセット"""
        self.used_words.clear()
        self.game_state = {
            "is_playing": False,
            "current_word": None,
            "turn_count": 0
        }
        self.history.clear()
        self.protocol.clear_history()

    def get_game_stats(self) -> Dict[str, Any]:
        """
        ゲーム統計を取得

        Returns:
            ゲーム統計
        """
        return {
            "agent_name": self.name,
            "turn_count": self.game_state["turn_count"],
            "used_words_count": len(self.used_words),
            "used_words": list(self.used_words),
            "history": self.history
        }
