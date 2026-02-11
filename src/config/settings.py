"""
アプリケーション設定

環境変数からアプリケーション設定を読み込みます。
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()


class Settings:
    """
    アプリケーション設定クラス

    環境変数から設定を読み込み、アプリケーション全体で
    使用できるようにします。

    Attributes:
        google_api_key (str): Google API Key
        google_project_id (str): Google Cloud プロジェクトID
        google_location (str): Google Cloud リージョン
        app_name (str): アプリケーション名
        app_env (str): 実行環境（development/production）
        log_level (str): ログレベル
        test_mode (bool): テストモードかどうか
    """

    def __init__(self):
        """設定の初期化"""
        # Google ADK設定
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.google_project_id: str = os.getenv("GOOGLE_PROJECT_ID", "")
        self.google_location: str = os.getenv("GOOGLE_LOCATION", "us-central1")

        # アプリケーション設定
        self.app_name: str = os.getenv("APP_NAME", "agent_shiritori")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # テスト設定
        self.test_mode: bool = os.getenv("TEST_MODE", "false").lower() == "true"

    def is_development(self) -> bool:
        """
        開発環境かどうかを判定

        Returns:
            開発環境の場合True
        """
        return self.app_env == "development"

    def is_production(self) -> bool:
        """
        本番環境かどうかを判定

        Returns:
            本番環境の場合True
        """
        return self.app_env == "production"

    def validate(self) -> bool:
        """
        設定の妥当性をチェック

        Returns:
            設定が有効な場合True

        Raises:
            ValueError: 必須の設定が不足している場合
        """
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEYが設定されていません")

        return True


# シングルトンインスタンス
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    設定のシングルトンインスタンスを取得

    Returns:
        設定インスタンス
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
