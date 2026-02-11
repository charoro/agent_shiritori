"""
Google ADKサービス

Google Agent Development Kitとの連携を行うサービスクラス
"""

from __future__ import annotations

import importlib.util
import os
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# google-genai パッケージの存在チェック
GENAI_AVAILABLE = importlib.util.find_spec("google.genai") is not None

if TYPE_CHECKING:
    from google import genai


class GoogleADKService:
    """
    Google ADKとの連携を行うサービスクラス

    このクラスは、Google Generative AI (google-genai) を使用して
    テキスト生成などのAI機能を提供します。
    クライアントは初回のAPI呼び出し時に遅延初期化されます。

    Attributes:
        api_key (str): Google API Key
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
        """
        Google ADKサービスの初期化

        Args:
            api_key: Google API Key（未指定の場合は環境変数から取得）
            model_name: 使用するモデル名（デフォルト: gemini-2.0-flash）
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._model_name = model_name
        self._client = None

    def _get_client(self) -> "genai.Client":
        """
        クライアントを遅延初期化して返す

        Returns:
            google.genai.Clientインスタンス

        Raises:
            ImportError: google-genaiパッケージがインストールされていない場合
            ValueError: API Keyが設定されていない場合
        """
        if self._client is None:
            if not GENAI_AVAILABLE:
                raise ImportError(
                    "google-genaiパッケージがインストールされていません。\n"
                    "pip install google-genai を実行してください。"
                )
            if not self.api_key:
                raise ValueError(
                    "GOOGLE_API_KEYが設定されていません。\n"
                    ".envファイルにGOOGLE_API_KEY=your_api_keyを追加してください。"
                )
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        テキストを生成

        Args:
            prompt: プロンプト
            max_tokens: 最大トークン数（オプション）
            temperature: 生成の多様性（0.0-1.0）

        Returns:
            生成されたテキスト

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            config_params: Dict[str, Any] = {
                "temperature": temperature,
            }
            if max_tokens:
                config_params["max_output_tokens"] = max_tokens

            from google.genai import types

            client = self._get_client()
            response = await client.aio.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**config_params)
            )
            text = response.text
            if text is None:
                raise Exception("レスポンスにテキストが含まれていません")
            return text.strip()
        except Exception as e:
            raise Exception(f"テキスト生成に失敗しました: {str(e)}")

    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        コンテキストを含めてテキストを生成

        Args:
            prompt: プロンプト
            context: 会話の履歴（[{"role": "user/assistant", "content": "..."}]形式）
            max_tokens: 最大トークン数（オプション）
            temperature: 生成の多様性（0.0-1.0）

        Returns:
            生成されたテキスト

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        # コンテキストを含めたプロンプトを構築
        context_text = "\n".join([
            f"{item['role']}: {item['content']}"
            for item in context
        ])

        full_prompt = f"{context_text}\n\nuser: {prompt}"

        return await self.generate_text(full_prompt, max_tokens, temperature)

    async def chat(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        チャット形式で対話

        Args:
            message: ユーザーのメッセージ
            chat_history: チャット履歴（オプション）

        Returns:
            AIの応答

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        if chat_history:
            return await self.generate_with_context(message, chat_history)
        else:
            return await self.generate_text(message)
