"""
基底エージェントクラス

すべてのAIエージェントが継承する基底クラスを定義します。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseAgent(ABC):
    """
    すべてのAIエージェントの基底クラス

    このクラスを継承して、独自のエージェントを実装します。

    Attributes:
        name (str): エージェントの名前
        config (Dict[str, Any]): エージェントの設定情報
        history (List[Dict[str, Any]]): 対話履歴
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        エージェントの初期化

        Args:
            name: エージェント名
            config: 設定情報（オプション）
        """
        self.name = name
        self.config = config or {}
        self.history: List[Dict[str, Any]] = []

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        入力データを処理してレスポンスを返す

        このメソッドは、サブクラスで必ず実装する必要があります。

        Args:
            input_data: 入力データ

        Returns:
            処理結果を含む辞書

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        pass

    def add_to_history(self, interaction: Dict[str, Any]) -> None:
        """
        対話履歴に追加

        Args:
            interaction: 対話の内容（input, output, timestampなど）
        """
        # タイムスタンプが含まれていない場合は追加
        if "timestamp" not in interaction:
            interaction["timestamp"] = datetime.now().isoformat()

        self.history.append(interaction)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        対話履歴を取得

        Returns:
            対話履歴のリスト（コピー）
        """
        return self.history.copy()

    def clear_history(self) -> None:
        """
        対話履歴をクリア
        """
        self.history.clear()

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得

        Args:
            key: 設定キー
            default: デフォルト値

        Returns:
            設定値
        """
        return self.config.get(key, default)

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        設定を更新

        Args:
            updates: 更新する設定の辞書
        """
        self.config.update(updates)

    def __repr__(self) -> str:
        """
        エージェントの文字列表現

        Returns:
            エージェントの情報を含む文字列
        """
        return f"{self.__class__.__name__}(name='{self.name}', history_length={len(self.history)})"
