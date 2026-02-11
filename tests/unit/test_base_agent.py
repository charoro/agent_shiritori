"""
BaseAgentクラスのユニットテスト

基底エージェントクラスの機能をテストします。
"""

import pytest
from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """テスト用のエージェント実装"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        テスト用の処理実装

        Args:
            input_data: 入力データ

        Returns:
            処理結果
        """
        return {
            "result": "processed",
            "input": input_data,
            "agent_name": self.name
        }


class TestBaseAgent:
    """BaseAgentクラスのテストスイート"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """エージェントの初期化テスト"""
        agent = TestAgent(name="TestAgent")

        assert agent.name == "TestAgent"
        assert agent.history == []
        assert agent.config == {}

    @pytest.mark.asyncio
    async def test_agent_initialization_with_config(self, test_config):
        """設定付きでのエージェント初期化テスト"""
        agent = TestAgent(name="TestAgent", config=test_config)

        assert agent.name == "TestAgent"
        assert agent.config == test_config
        assert agent.get_config("temperature") == 0.7

    @pytest.mark.asyncio
    async def test_agent_process(self):
        """エージェントの処理機能テスト"""
        agent = TestAgent(name="TestAgent")
        input_data = {"test": "data", "value": 123}

        result = await agent.process(input_data)

        assert result["result"] == "processed"
        assert result["input"] == input_data
        assert result["agent_name"] == "TestAgent"

    @pytest.mark.asyncio
    async def test_add_to_history(self, sample_interaction):
        """履歴追加機能のテスト"""
        agent = TestAgent(name="TestAgent")

        agent.add_to_history(sample_interaction)
        history = agent.get_history()

        assert len(history) == 1
        assert history[0] == sample_interaction

    @pytest.mark.asyncio
    async def test_add_to_history_auto_timestamp(self):
        """タイムスタンプ自動追加のテスト"""
        agent = TestAgent(name="TestAgent")
        interaction = {"input": "test", "output": "result"}

        agent.add_to_history(interaction)
        history = agent.get_history()

        assert len(history) == 1
        assert "timestamp" in history[0]

    @pytest.mark.asyncio
    async def test_get_history(self):
        """履歴取得機能のテスト"""
        agent = TestAgent(name="TestAgent")

        # 複数の対話を追加
        for i in range(3):
            agent.add_to_history({
                "input": f"input_{i}",
                "output": f"output_{i}"
            })

        history = agent.get_history()
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_clear_history(self):
        """履歴クリア機能のテスト"""
        agent = TestAgent(name="TestAgent")

        # 履歴を追加
        agent.add_to_history({"input": "test", "output": "result"})
        assert len(agent.get_history()) == 1

        # 履歴をクリア
        agent.clear_history()
        assert len(agent.get_history()) == 0

    @pytest.mark.asyncio
    async def test_get_config(self, test_config):
        """設定取得機能のテスト"""
        agent = TestAgent(name="TestAgent", config=test_config)

        assert agent.get_config("temperature") == 0.7
        assert agent.get_config("max_tokens") == 1000
        assert agent.get_config("non_existent_key") is None
        assert agent.get_config("non_existent_key", "default") == "default"

    @pytest.mark.asyncio
    async def test_update_config(self):
        """設定更新機能のテスト"""
        agent = TestAgent(name="TestAgent", config={"key1": "value1"})

        # 設定を更新
        agent.update_config({"key2": "value2", "key3": "value3"})

        assert agent.get_config("key1") == "value1"
        assert agent.get_config("key2") == "value2"
        assert agent.get_config("key3") == "value3"

    @pytest.mark.asyncio
    async def test_agent_repr(self):
        """文字列表現のテスト"""
        agent = TestAgent(name="TestAgent")
        agent.add_to_history({"input": "test", "output": "result"})

        repr_str = repr(agent)

        assert "TestAgent" in repr_str
        assert "name='TestAgent'" in repr_str
        assert "history_length=1" in repr_str
