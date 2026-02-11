"""
シンプルなエージェントの使用例

基本的なエージェントの実装と使用方法を示します。
"""

import asyncio
from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class SimpleGreetingAgent(BaseAgent):
    """
    シンプルな挨拶エージェント

    ユーザーの名前を受け取り、挨拶を返すエージェント
    """

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        挨拶メッセージを生成

        Args:
            input_data: {"name": "ユーザー名"}

        Returns:
            挨拶メッセージを含む辞書
        """
        name = input_data.get("name", "ゲスト")

        # 挨拶メッセージを生成
        greeting = f"こんにちは、{name}さん！"

        # 履歴に追加
        self.add_to_history({
            "input": name,
            "output": greeting
        })

        return {
            "greeting": greeting,
            "name": name,
            "message_count": len(self.history)
        }


async def main():
    """
    メイン実行関数

    エージェントを作成して使用する例を示します。
    """
    print("=" * 50)
    print("シンプルなエージェントの使用例")
    print("=" * 50)

    # エージェントの作成
    agent = SimpleGreetingAgent(
        name="GreetingAgent",
        config={"language": "ja"}
    )

    print(f"\nエージェント作成: {agent}")

    # ユーザー名のリスト
    names = ["太郎", "花子", "次郎"]

    # 各ユーザーに挨拶
    for name in names:
        print(f"\n--- {name}さんへの挨拶 ---")

        result = await agent.process({"name": name})

        print(f"挨拶: {result['greeting']}")
        print(f"メッセージ数: {result['message_count']}")

    # 履歴の表示
    print("\n--- 対話履歴 ---")
    for i, interaction in enumerate(agent.get_history(), 1):
        print(f"{i}. 入力: {interaction['input']}")
        print(f"   出力: {interaction['output']}")
        print(f"   時刻: {interaction['timestamp']}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    # 非同期関数を実行
    asyncio.run(main())
