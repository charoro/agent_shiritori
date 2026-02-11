"""
しりとりゲーム実行プログラム

ノエルとフレアの2つのAIエージェントがA2Aプロトコルを使って
日本語のしりとりゲームを行います。
"""

import asyncio
import os
import argparse
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from src.agents.shiritori_agent import ShiritoriAgent
from src.models.a2a_message import MessageType

# 環境変数を読み込み
load_dotenv()


class ShiritoriGame:
    """
    しりとりゲーム管理クラス

    2つのエージェント間のしりとりゲームを管理します。

    Attributes:
        agent1: 最初のエージェント（ノエル）
        agent2: 2番目のエージェント（フレア）
        max_turns: 最大ターン数
        timeout: レスポンスタイムアウト（秒）
        game_log: ゲームログ
    """

    def __init__(
        self,
        agent1_name: str = "ノエル",
        agent2_name: str = "フレア",
        max_turns: int = 20,
        timeout: float = 180.0
    ):
        """
        ゲームの初期化

        Args:
            agent1_name: エージェント1の名前
            agent2_name: エージェント2の名前
            max_turns: 最大ターン数
            timeout: レスポンスタイムアウト（秒）
        """
        self.agent1 = ShiritoriAgent(name=agent1_name, timeout=timeout)
        self.agent2 = ShiritoriAgent(name=agent2_name, timeout=timeout)
        self.max_turns = max_turns
        self.timeout = timeout
        self.game_log = []
        self.winner: Optional[str] = None
        self.game_result: Optional[str] = None

    def _print_header(self) -> None:
        """ゲームヘッダーを表示"""
        print("=" * 80)
        print("🎮 しりとりゲーム - A2Aプロトコル版")
        print("=" * 80)
        print(f"参加者: {self.agent1.name} 🆚 {self.agent2.name}")
        print(f"最大ターン数: {self.max_turns}")
        print(f"タイムアウト: {self.timeout}秒")
        print("=" * 80)
        print()

    def _print_turn(
        self,
        turn: int,
        agent_name: str,
        word: str,
        elapsed_time: float
    ) -> None:
        """
        ターン情報を表示

        Args:
            turn: ターン番号
            agent_name: エージェント名
            word: 発言した単語
            elapsed_time: 経過時間（秒）
        """
        print(f"ターン {turn:3d} | {agent_name:8s} | 「{word}」 ({elapsed_time:.2f}秒)")

    def _print_game_over(
        self,
        reason: str,
        winner: Optional[str] = None
    ) -> None:
        """
        ゲーム終了メッセージを表示

        Args:
            reason: 終了理由
            winner: 勝者（引き分けの場合はNone）
        """
        print()
        print("=" * 80)
        print("🏁 ゲーム終了")
        print("=" * 80)
        print(f"終了理由: {reason}")

        if winner:
            print(f"🎉 勝者: {winner}")
        else:
            print("🤝 引き分け")

        print("=" * 80)

    def _print_statistics(self) -> None:
        """ゲーム統計を表示"""
        print()
        print("📊 ゲーム統計")
        print("-" * 80)

        # エージェント1の統計
        stats1 = self.agent1.get_game_stats()
        print(f"{stats1['agent_name']}:")
        print(f"  - 発言回数: {len([h for h in stats1['history'] if h['agent'] == stats1['agent_name']])}")
        print(f"  - 使用単語: {', '.join([h['word'] for h in stats1['history'] if h['agent'] == stats1['agent_name']])}")

        # エージェント2の統計
        stats2 = self.agent2.get_game_stats()
        print(f"{stats2['agent_name']}:")
        print(f"  - 発言回数: {len([h for h in stats2['history'] if h['agent'] == stats2['agent_name']])}")
        print(f"  - 使用単語: {', '.join([h['word'] for h in stats2['history'] if h['agent'] == stats2['agent_name']])}")

        # 全体統計
        all_words = stats1['used_words'] + stats2['used_words']
        unique_words = set(all_words)
        print(f"\n総ターン数: {len(self.game_log)}")
        print(f"使用単語数: {len(unique_words)}")
        print(f"全使用単語: {' → '.join([log['word'] for log in self.game_log])}")

        print("-" * 80)

    async def play(self) -> Dict[str, Any]:
        """
        ゲームを開始して実行

        Returns:
            ゲーム結果
        """
        self._print_header()

        try:
            # ゲーム開始：ノエルが最初の単語を発言
            print("🎬 ゲーム開始！")
            print()

            start_time = datetime.now()
            result = await self.agent1.process({
                "action": "start",
                "opponent": self.agent2.name
            })
            elapsed = (datetime.now() - start_time).total_seconds()

            if not result["success"]:
                self._print_game_over(
                    reason=f"ゲーム開始に失敗: {result.get('error')}",
                    winner=self.agent2.name
                )
                return {
                    "winner": self.agent2.name,
                    "reason": result.get("error"),
                    "turns": 0
                }

            current_word = result["word"]
            current_turn = 1

            self._print_turn(current_turn, self.agent1.name, current_word, elapsed)
            self.game_log.append({
                "turn": current_turn,
                "agent": self.agent1.name,
                "word": current_word,
                "elapsed_time": elapsed
            })

            # ゲームループ
            current_agent = self.agent2
            opponent_agent = self.agent1

            while current_turn < self.max_turns:
                current_turn += 1

                # 現在のエージェントが応答
                start_time = datetime.now()
                result = await current_agent.process({
                    "action": "respond",
                    "word": current_word,
                    "opponent": opponent_agent.name
                })
                elapsed = (datetime.now() - start_time).total_seconds()

                # エラーチェック
                if not result["success"]:
                    error_msg = result.get("error", "不明なエラー")
                    print()
                    print(f"❌ {current_agent.name} がエラー: {error_msg}")

                    # ゲーム終了判定
                    if result.get("is_game_over", False):
                        winner = result.get("winner", opponent_agent.name)
                        self.winner = winner
                        self.game_result = error_msg

                        self._print_game_over(
                            reason=error_msg,
                            winner=winner
                        )
                        self._print_statistics()

                        return {
                            "winner": winner,
                            "reason": error_msg,
                            "turns": current_turn - 1,
                            "game_log": self.game_log
                        }

                    # それ以外のエラーは続行
                    continue

                # 成功した場合
                current_word = result["word"]

                self._print_turn(current_turn, current_agent.name, current_word, elapsed)
                self.game_log.append({
                    "turn": current_turn,
                    "agent": current_agent.name,
                    "word": current_word,
                    "elapsed_time": elapsed
                })

                # 「ん」で終わったかチェック
                if current_word[-1] == 'ん':
                    self.winner = opponent_agent.name
                    self.game_result = f"{current_agent.name}が「ん」で終わる単語を言いました"

                    self._print_game_over(
                        reason=self.game_result,
                        winner=self.winner
                    )
                    self._print_statistics()

                    return {
                        "winner": self.winner,
                        "reason": self.game_result,
                        "turns": current_turn,
                        "game_log": self.game_log
                    }

                # エージェントを交代
                current_agent, opponent_agent = opponent_agent, current_agent

            # 最大ターン数に達した場合は引き分け
            self.game_result = f"最大ターン数（{self.max_turns}）に達しました"
            self._print_game_over(reason=self.game_result, winner=None)
            self._print_statistics()

            return {
                "winner": None,
                "reason": self.game_result,
                "turns": current_turn,
                "game_log": self.game_log,
                "result": "draw"
            }

        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            self._print_game_over(reason=error_msg)
            return {
                "winner": None,
                "reason": error_msg,
                "turns": len(self.game_log),
                "game_log": self.game_log,
                "result": "error"
            }


async def main():
    """
    メイン実行関数

    コマンドライン引数と環境変数を処理してゲームを開始します。
    """
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(
        description="AIエージェント同士のしりとりゲーム"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=int(os.getenv("SHIRITORI_MAX_TURNS", "20")),
        help="最大ターン数（デフォルト: 20、環境変数: SHIRITORI_MAX_TURNS）"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("SHIRITORI_TIMEOUT", "180.0")),
        help="応答タイムアウト秒数（デフォルト: 180.0、環境変数: SHIRITORI_TIMEOUT）"
    )
    parser.add_argument(
        "--agent1-name",
        type=str,
        default=os.getenv("AGENT1_NAME", "ノエル"),
        help="エージェント1の名前（デフォルト: ノエル、環境変数: AGENT1_NAME）"
    )
    parser.add_argument(
        "--agent2-name",
        type=str,
        default=os.getenv("AGENT2_NAME", "フレア"),
        help="エージェント2の名前（デフォルト: フレア、環境変数: AGENT2_NAME）"
    )

    args = parser.parse_args()

    # ゲームを作成して実行
    game = ShiritoriGame(
        agent1_name=args.agent1_name,
        agent2_name=args.agent2_name,
        max_turns=args.max_turns,
        timeout=args.timeout
    )

    result = await game.play()

    # 結果をログに出力（オプション）
    if os.getenv("SAVE_GAME_LOG", "false").lower() == "true":
        import json
        log_file = f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📝 ゲームログを保存しました: {log_file}")


if __name__ == "__main__":
    # 非同期関数を実行
    asyncio.run(main())
