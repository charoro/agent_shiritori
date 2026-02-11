"""
しりとりエージェントのユニットテスト

ShiritoriAgentクラスの主要な機能をテストします。
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.shiritori_agent import ShiritoriAgent
from src.models.a2a_message import MessageType


class TestShiritoriAgent:
    """しりとりエージェントのテストクラス"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """エージェントの初期化テスト"""
        agent = ShiritoriAgent(name="テストエージェント", timeout=5.0)

        assert agent.name == "テストエージェント"
        assert agent.timeout == 5.0
        assert len(agent.used_words) == 0
        assert agent.game_state["turn_count"] == 0

    @pytest.mark.asyncio
    async def test_clean_word(self):
        """単語のクリーニング機能テスト"""
        agent = ShiritoriAgent(name="テスト")

        # 正常な単語
        assert agent._clean_word("りんご") == "りんご"

        # 句読点を含む
        assert agent._clean_word("りんご。") == "りんご"

        # 空白を含む
        assert agent._clean_word("り ん ご") == "りんご"

        # 改行を含む
        assert agent._clean_word("りんご\n") == "りんご"

    @pytest.mark.asyncio
    async def test_is_valid_word(self):
        """単語の妥当性検証テスト"""
        agent = ShiritoriAgent(name="テスト")

        # 有効な単語
        assert agent._is_valid_word("りんご") is True
        assert agent._is_valid_word("ごりら") is True

        # 無効な単語
        assert agent._is_valid_word("") is False  # 空文字
        assert agent._is_valid_word("apple") is False  # 英語
        assert agent._is_valid_word("リンゴ") is False  # カタカナ
        assert agent._is_valid_word("林檎") is False  # 漢字

    @pytest.mark.asyncio
    async def test_validate_previous_word(self):
        """前の単語の検証テスト"""
        agent = ShiritoriAgent(name="テスト")

        # 有効な単語
        result = agent._validate_previous_word("りんご")
        assert result["valid"] is True

        # 「ん」で終わる単語
        result = agent._validate_previous_word("みかん")
        assert result["valid"] is False
        assert "ん" in result["reason"]

        # 無効な単語
        result = agent._validate_previous_word("apple")
        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_reset_game(self):
        """ゲームリセット機能テスト"""
        agent = ShiritoriAgent(name="テスト")

        # ゲーム状態を変更
        agent.used_words.add("りんご")
        agent.game_state["turn_count"] = 5
        agent.add_to_history({"test": "data"})

        # リセット
        agent.reset_game()

        assert len(agent.used_words) == 0
        assert agent.game_state["turn_count"] == 0
        assert len(agent.history) == 0

    @pytest.mark.asyncio
    async def test_get_game_stats(self):
        """ゲーム統計取得テスト"""
        agent = ShiritoriAgent(name="テスト")

        agent.used_words.add("りんご")
        agent.used_words.add("ごりら")
        agent.game_state["turn_count"] = 2

        stats = agent.get_game_stats()

        assert stats["agent_name"] == "テスト"
        assert stats["turn_count"] == 2
        assert stats["used_words_count"] == 2
        assert "りんご" in stats["used_words"]
        assert "ごりら" in stats["used_words"]

    @pytest.mark.asyncio
    async def test_start_game_with_mock(self):
        """ゲーム開始のモックテスト"""
        agent = ShiritoriAgent(name="ノエル")

        # Google ADKサービスをモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="りんご")
        ):
            result = await agent.process({
                "action": "start",
                "opponent": "フレア"
            })

            assert result["success"] is True
            assert result["word"] == "りんご"
            assert "りんご" in agent.used_words

    @pytest.mark.asyncio
    async def test_respond_to_word_with_mock(self):
        """単語応答のモックテスト"""
        agent = ShiritoriAgent(name="フレア")

        # Google ADKサービスをモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="ごりら")
        ):
            result = await agent.process({
                "action": "respond",
                "word": "りんご",
                "opponent": "ノエル"
            })

            assert result["success"] is True
            assert result["word"] == "ごりら"
            assert "りんご" in agent.used_words
            assert "ごりら" in agent.used_words
            assert result["is_game_over"] is False

    @pytest.mark.asyncio
    async def test_respond_with_n_ending(self):
        """「ん」で終わる単語の応答テスト"""
        agent = ShiritoriAgent(name="フレア")

        # 「ん」で終わる単語を返すようモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="らっぱ")
        ):
            # 最初に「ぱ」で始まる単語に応答
            result1 = await agent.process({
                "action": "respond",
                "word": "えんぴつ",  # 実際は「つ」で終わる
                "opponent": "ノエル"
            })

        # 次に「ん」で終わる単語を返すようモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="みかん")
        ):
            result2 = await agent.process({
                "action": "respond",
                "word": "かめ",
                "opponent": "ノエル"
            })

            # 「ん」で終わったのでゲームオーバー
            assert result2["success"] is False
            assert result2["is_game_over"] is True
            assert result2["winner"] == "ノエル"

    @pytest.mark.asyncio
    async def test_respond_with_duplicate_word(self):
        """重複単語の応答テスト"""
        agent = ShiritoriAgent(name="フレア")

        # 既に使用済みの単語を追加
        agent.used_words.add("ごりら")

        # 同じ単語を返すようモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="ごりら")
        ):
            result = await agent.process({
                "action": "respond",
                "word": "りんご",
                "opponent": "ノエル"
            })

            # 重複単語なのでゲームオーバー
            assert result["success"] is False
            assert result["is_game_over"] is True
            assert "既に使われた" in result["error"]

    @pytest.mark.asyncio
    async def test_respond_with_wrong_starting_char(self):
        """間違った文字で始まる単語の応答テスト"""
        agent = ShiritoriAgent(name="フレア")

        # 間違った文字で始まる単語を返すようモック
        with patch.object(
            agent.adk_service,
            'generate_text',
            new=AsyncMock(return_value="たぬき")  # 「ご」で始まるべきなのに「た」
        ):
            result = await agent.process({
                "action": "respond",
                "word": "りんご",
                "opponent": "ノエル"
            })

            # 間違った文字で始まったのでゲームオーバー
            assert result["success"] is False
            assert result["is_game_over"] is True
            assert "始まっていません" in result["error"]


class TestA2AMessageIntegration:
    """A2Aメッセージ統合テスト"""

    @pytest.mark.asyncio
    async def test_protocol_message_handling(self):
        """A2Aプロトコルのメッセージハンドリングテスト"""
        agent = ShiritoriAgent(name="ノエル")

        # プロトコルが正しく初期化されているか
        assert agent.protocol is not None
        assert agent.protocol.agent_name == "ノエル"

        # ハンドラーが登録されているか
        assert MessageType.REQUEST.value in agent.protocol.handlers
