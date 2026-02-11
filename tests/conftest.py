"""
Pytestフィクスチャ

テスト全体で使用される共通のフィクスチャを定義します。
"""

import pytest
import os
from typing import Dict, Any


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """
    テスト用の設定を提供するフィクスチャ

    Returns:
        テスト用設定の辞書
    """
    return {
        "model_name": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 1000,
    }


@pytest.fixture
def mock_google_api_key(monkeypatch) -> str:
    """
    モックのGoogle APIキーを設定するフィクスチャ

    Args:
        monkeypatch: pytestのmonkeypatchフィクスチャ

    Returns:
        モックのAPIキー
    """
    mock_key = "test_api_key_12345"
    monkeypatch.setenv("GOOGLE_API_KEY", mock_key)
    return mock_key


@pytest.fixture
def sample_interaction() -> Dict[str, Any]:
    """
    サンプルの対話データを提供するフィクスチャ

    Returns:
        対話データの辞書
    """
    return {
        "input": "テスト入力",
        "output": "テスト出力",
        "timestamp": "2026-02-10T00:00:00"
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    テスト環境を自動的にセットアップするフィクスチャ

    各テストの実行前に、テスト用の環境変数を設定します。

    Args:
        monkeypatch: pytestのmonkeypatchフィクスチャ
    """
    # テスト用環境変数の設定
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
