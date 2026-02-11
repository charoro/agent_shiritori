# Agent Shiritori - Google ADK AIエージェントプロジェクト

Google Agent Development Kit (ADK)を使用したPythonベースのAIエージェント開発プロジェクトです。

## プロジェクト概要

このプロジェクトは、Google ADKを活用して、インテリジェントなAIエージェントを開発するためのテンプレートとベストプラクティスを提供します。しりとりゲームを例として、エージェントの設計、実装、テストの方法を示しています。

## 特徴

- 🤖 Google ADKを使用した高度なAIエージェント
- 🧪 包括的なテストスイート（ユニット、統合、E2Eテスト）
- 📝 完全な日本語ドキュメント
- 🔧 開発環境のセットアップが簡単
- 📊 コードカバレッジレポート
- 🎯 ベストプラクティスに基づいた設計

## クイックスタート

### 1. リポジトリのクローン

```bash
cd /home/charoro/git/agent_shiritori
```

### 2. 仮想環境のセットアップ

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. 環境変数の設定

`.env`ファイルを作成して、Google APIキーを設定します：

```bash
echo "GOOGLE_API_KEY=your_api_key_here" > .env
echo "GOOGLE_PROJECT_ID=your_project_id" >> .env
```

### 5. テストの実行

```bash
pytest
```

## プロジェクト構造

詳細なプロジェクト構造とファイルの説明は、[AGENTS.md](AGENTS.md)を参照してください。

```txt
agent_shiritori/
├── src/              # ソースコード
│   ├── agents/       # エージェント実装
│   ├── models/       # データモデル
│   ├── services/     # 外部サービス連携
│   └── config/       # 設定管理
├── tests/            # テストコード
│   ├── unit/         # ユニットテスト
│   ├── integration/  # 統合テスト
│   └── e2e/          # E2Eテスト
└── examples/         # 使用例
```

## 開発ガイド

詳細な開発ガイドは[AGENTS.md](AGENTS.md)を参照してください。以下は基本的なワークフローです：

### エージェントの作成

```python
from src.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    async def process(self, input_data):
        # エージェントのロジックを実装
        return {"result": "処理結果"}
```

### テストの作成

```python
import pytest
from src.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_my_agent():
    agent = MyAgent(name="TestAgent")
    result = await agent.process({"input": "test"})
    assert result["result"] == "処理結果"
```

## しりとりゲームの実行

このプロジェクトには、2つのAIエージェント（ノエルとフレア）がA2Aプロトコルを使って日本語のしりとりゲームを行うデモが含まれています。

### 基本的な実行方法

```bash
python shiritori_game.py
```

### オプション付き実行

```bash
# 最大ターン数を30に設定
python shiritori_game.py --max-turns 30

# タイムアウトを15秒に設定
python shiritori_game.py --timeout 15.0

# エージェント名をカスタマイズ
python shiritori_game.py --agent1-name "太郎" --agent2-name "花子"

# すべてのオプションを組み合わせ
python shiritori_game.py --max-turns 50 --timeout 20.0 --agent1-name "Alice" --agent2-name "Bob"
```

### 環境変数での設定

`.env`ファイルで設定を管理することもできます：

```bash
# .envファイルに追加
SHIRITORI_MAX_TURNS=30
SHIRITORI_TIMEOUT=15.0
AGENT1_NAME=太郎
AGENT2_NAME=花子
SAVE_GAME_LOG=true  # ゲームログをJSONファイルに保存
```

### ゲームのルール

1. ノエルが最初の単語を発言します
2. フレアがその単語の最後の文字で始まる単語を返します
3. 交互に単語を発言し続けます
4. 以下の場合にゲームが終了します：
   - 「ん」で終わる単語を言った場合（負け）
   - 3分以内に応答できなかった場合（負け）
   - 既に使用済みの単語を使った場合（負け）
   - 最大ターン数に達した場合（引き分け）

## コマンド

### テスト関連

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=src --cov-report=html

# 特定のテストのみ実行
pytest tests/unit/

# 詳細な出力で実行
pytest -v
```

### コード品質

```bash
# コードフォーマット
black src/ tests/

# リント
flake8 src/ tests/

# 型チェック
mypy src/
```

## ドキュメント

- [AGENTS.md](AGENTS.md) - 開発ガイドとベストプラクティス
- `docs/architecture.md` - アーキテクチャ設計（作成予定）
- `docs/api_reference.md` - APIリファレンス（作成予定）

## 要件

- Python 3.10以上
- Google Cloud アカウント
- Google API Key

## ライセンス

MIT License

## コントリビューション

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

## サポート

問題や質問がある場合は、Issueを作成してください。

## 作者

開発者: charoro

## 更新履歴

- 2026-02-10: プロジェクト初期セットアップ
