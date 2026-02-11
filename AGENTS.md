# Google ADK AIエージェント開発ガイド

## プロジェクト概要

このプロジェクトは、Google Agent Development Kit (ADK)を使用してPythonベースのAIエージェントを開発するためのものです。AIエージェントの開発、テスト、デプロイメントの標準化されたワークフローを提供します。

## 前提条件

- Python 3.10以上
- pip（Pythonパッケージマネージャー）
- Git
- Google Cloud アカウント（ADK利用のため）
- テキストエディタまたはIDE（VS Code推奨）

## 環境セットアップ

### 1. 仮想環境の作成

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Linux/Mac）
source venv/bin/activate

# 仮想環境の有効化（Windows）
venv\Scripts\activate
```

### 2. 必要なパッケージのインストール

```bash
# 基本パッケージのインストール
pip install --upgrade pip
pip install google-cloud-aiplatform
pip install google-generativeai
pip install python-dotenv

# 開発・テスト用パッケージのインストール
pip install pytest
pip install pytest-cov
pip install pytest-asyncio
pip install black
pip install flake8
pip install pyright
```

### 3. 環境変数の設定

`.env`ファイルを作成して、必要な環境変数を設定します：

```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_LOCATION=us-central1
```

## プロジェクト構造

```txt
agent_shiritori/
├── AGENTS.md                 # このファイル
├── README.md                 # プロジェクトのREADME
├── .env                      # 環境変数（Gitで管理しない）
├── .gitignore               # Git除外ファイル
├── requirements.txt         # 依存パッケージリスト
├── requirements-dev.txt     # 開発用依存パッケージ
├── pytest.ini              # Pytestの設定ファイル
├── .flake8                 # Flake8の設定ファイル
├── mypy.ini                # Mypyの設定ファイル
│
├── src/                    # ソースコードディレクトリ
│   ├── __init__.py
│   ├── agents/            # エージェント実装
│   │   ├── __init__.py
│   │   ├── base_agent.py      # 基底エージェントクラス
│   │   ├── shiritori_agent.py # しりとりエージェント（例）
│   │   └── utils.py           # ユーティリティ関数
│   │
│   ├── models/            # データモデル
│   │   ├── __init__.py
│   │   └── message.py         # メッセージモデル
│   │
│   ├── services/          # 外部サービス連携
│   │   ├── __init__.py
│   │   └── google_adk.py      # Google ADK連携
│   │
│   └── config/            # 設定管理
│       ├── __init__.py
│       └── settings.py        # アプリケーション設定
│
├── tests/                 # テストコード
│   ├── __init__.py
│   ├── conftest.py           # Pytestのフィクスチャ
│   ├── unit/                 # ユニットテスト
│   │   ├── __init__.py
│   │   ├── test_base_agent.py
│   │   └── test_utils.py
│   │
│   ├── integration/          # 統合テスト
│   │   ├── __init__.py
│   │   └── test_agent_integration.py
│   │
│   └── e2e/                  # エンドツーエンドテスト
│       ├── __init__.py
│       └── test_full_workflow.py
│
├── examples/              # 使用例
│   ├── __init__.py
│   ├── simple_agent.py       # シンプルなエージェント例
│   └── advanced_agent.py     # 高度なエージェント例
│
└── docs/                  # ドキュメント
    ├── architecture.md       # アーキテクチャ設計
    ├── api_reference.md      # APIリファレンス
    └── development_guide.md  # 開発ガイド
```

## エージェントの開発方法

### 1. 基底エージェントクラスの理解

すべてのエージェントは`BaseAgent`クラスを継承します：

```python
# src/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """
    すべてのAIエージェントの基底クラス

    このクラスを継承して、独自のエージェントを実装します。
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
        self.history = []

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        入力データを処理してレスポンスを返す

        Args:
            input_data: 入力データ

        Returns:
            処理結果
        """
        pass

    def add_to_history(self, interaction: Dict[str, Any]) -> None:
        """
        対話履歴に追加

        Args:
            interaction: 対話の内容
        """
        self.history.append(interaction)

    def get_history(self) -> list:
        """
        対話履歴を取得

        Returns:
            対話履歴のリスト
        """
        return self.history.copy()
```

### 2. カスタムエージェントの実装

```python
# src/agents/shiritori_agent.py

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent
from ..services.google_adk import GoogleADKService

class ShiritoriAgent(BaseAgent):
    """
    しりとりゲームを行うAIエージェント
    """

    def __init__(self, name: str = "ShiritoriAgent"):
        super().__init__(name)
        self.adk_service = GoogleADKService()
        self.used_words = set()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        しりとりの入力を処理して次の単語を返す

        Args:
            input_data: {"word": "入力された単語"}

        Returns:
            {"word": "次の単語", "is_valid": True/False}
        """
        word = input_data.get("word", "").strip()

        # 入力の検証
        if not word:
            return {
                "word": None,
                "is_valid": False,
                "error": "単語が入力されていません"
            }

        # 使用済み単語のチェック
        if word in self.used_words:
            return {
                "word": None,
                "is_valid": False,
                "error": "その単語は既に使われています"
            }

        # 最後の文字を取得
        last_char = word[-1]

        # Google ADKを使用して次の単語を生成
        prompt = f"しりとりゲームで「{word}」の次に続く単語を1つだけ答えてください。「{last_char}」で始まる単語を選んでください。"
        next_word = await self.adk_service.generate_text(prompt)

        # 履歴に追加
        self.used_words.add(word)
        self.used_words.add(next_word)

        interaction = {
            "input": word,
            "output": next_word,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.add_to_history(interaction)

        return {
            "word": next_word,
            "is_valid": True,
            "previous_word": word
        }
```

### 3. Google ADKサービスの実装

```python
# src/services/google_adk.py

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GoogleADKService:
    """
    Google ADKとの連携を行うサービスクラス
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Google ADKサービスの初期化

        Args:
            api_key: Google API Key（未指定の場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEYが設定されていません")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_text(self, prompt: str) -> str:
        """
        テキストを生成

        Args:
            prompt: プロンプト

        Returns:
            生成されたテキスト
        """
        response = await self.model.generate_content_async(prompt)
        return response.text.strip()

    async def generate_with_context(
        self,
        prompt: str,
        context: list
    ) -> str:
        """
        コンテキストを含めてテキストを生成

        Args:
            prompt: プロンプト
            context: 会話の履歴

        Returns:
            生成されたテキスト
        """
        # コンテキストを含めたプロンプトを構築
        full_prompt = "\n".join([
            "過去の会話:",
            *[f"- {item}" for item in context],
            f"\n現在の質問: {prompt}"
        ])

        return await self.generate_text(full_prompt)
```

## テストの実施方法

### 1. テスト環境の準備

```bash
# テスト用環境変数の設定（.env.testファイルを作成）
cp .env .env.test
```

### 2. ユニットテストの作成

```python
# tests/unit/test_base_agent.py

import pytest
from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    """テスト用のエージェント実装"""

    async def process(self, input_data):
        return {"result": "processed", "input": input_data}

@pytest.mark.asyncio
async def test_agent_initialization():
    """エージェントの初期化テスト"""
    agent = TestAgent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.history == []

@pytest.mark.asyncio
async def test_agent_process():
    """エージェントの処理機能テスト"""
    agent = TestAgent(name="TestAgent")
    result = await agent.process({"test": "data"})
    assert result["result"] == "processed"
    assert result["input"]["test"] == "data"

@pytest.mark.asyncio
async def test_agent_history():
    """履歴管理機能のテスト"""
    agent = TestAgent(name="TestAgent")

    interaction = {"input": "test", "output": "result"}
    agent.add_to_history(interaction)

    history = agent.get_history()
    assert len(history) == 1
    assert history[0] == interaction
```

### 3. 統合テストの作成

```python
# tests/integration/test_agent_integration.py

import pytest
from src.agents.shiritori_agent import ShiritoriAgent

@pytest.mark.asyncio
async def test_shiritori_agent_full_workflow():
    """しりとりエージェントの完全なワークフローテスト"""
    agent = ShiritoriAgent()

    # 最初の単語を入力
    result1 = await agent.process({"word": "りんご"})
    assert result1["is_valid"] is True
    assert result1["word"] is not None

    # 次の単語を入力
    next_word = result1["word"]
    result2 = await agent.process({"word": next_word})
    assert result2["is_valid"] is True

@pytest.mark.asyncio
async def test_shiritori_duplicate_word():
    """重複単語の検証テスト"""
    agent = ShiritoriAgent()

    # 同じ単語を2回使用
    await agent.process({"word": "りんご"})
    result = await agent.process({"word": "りんご"})

    assert result["is_valid"] is False
    assert "既に使われています" in result["error"]
```

### 4. テストの実行

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=src --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/unit/test_base_agent.py

# 詳細な出力で実行
pytest -v

# 特定のテストマークのみ実行
pytest -m asyncio
```

### 5. 継続的なテスト

```bash
# ファイル変更を監視して自動的にテストを実行
pytest-watch
```

## コード品質管理

### 1. コードフォーマット

```bash
# Blackでコードを自動フォーマット
black src/ tests/

# フォーマットのチェックのみ
black --check src/ tests/
```

### 2. リント

```bash
# Flake8でコードをチェック
flake8 src/ tests/

# 特定のエラーを無視
flake8 --ignore=E501,W503 src/
```

### 3. 静的解析（Pyright）

本プロジェクトでは静的解析ツールとして **Pyright** を使用します。

```bash
# Pyrightで静的解析を実行
pyright src/

# 特定のファイルのみチェック
pyright src/services/google_adk.py
```

Pyrightのインストール:

```bash
pip install pyright
```

### 4. ソースコード完了基準

ソースコードの作成・修正は、以下のすべての条件を満たした時点で完了とします。

1. **Pyrightによる静的解析をパスすること**
   - `pyright src/` を実行し、error および warning が **0件** であること
   - 型ヒントの不整合、未バインド変数、属性アクセスの問題がないこと
2. **Pytestによるテストをパスすること**
   - `pytest` を実行し、すべてのテストが成功すること
3. **コードフォーマットが統一されていること**
   - `black --check src/ tests/` でフォーマット違反がないこと

上記を満たさない状態のコードはレビュー対象外とします。CIパイプラインでも同様のチェックを実施します。

```bash
# ソースコード完了確認の一括実行例
pyright src/ && black --check src/ tests/ && pytest
```

## ベストプラクティス

### 1. エージェント設計の原則

- **単一責任の原則**: 各エージェントは1つの明確な目的を持つ
- **非同期処理**: I/O操作には`async/await`を使用
- **エラーハンドリング**: 適切な例外処理を実装
- **ログ記録**: 重要な操作はログに記録
- **テスト可能性**: モックやフィクスチャを活用した設計

### 2. コーディング規約

- **命名規則**:
  - クラス名: PascalCase（例: `ShiritoriAgent`）
  - 関数名: snake_case（例: `process_input`）
  - 定数: UPPER_SNAKE_CASE（例: `MAX_RETRIES`）
- **ドキュメント**: すべての公開関数にdocstringを記述
- **型ヒント**: 関数の引数と戻り値に型ヒントを付与
- **インポート順序**: 標準ライブラリ → サードパーティ → ローカル

### 3. テスト戦略

- **テストピラミッド**: ユニットテスト（多）> 統合テスト（中）> E2Eテスト（少）
- **テストカバレッジ**: 最低80%を目標
- **モック活用**: 外部APIはモックを使用
- **テストデータ**: フィクスチャで管理

### 4. セキュリティ

- **APIキーの管理**: 環境変数で管理、Gitにコミットしない
- **入力検証**: ユーザー入力は必ず検証
- **エラーメッセージ**: 機密情報を含めない
- **依存関係**: 定期的にセキュリティアップデート

## トラブルシューティング

### よくある問題と解決方法

#### 1. APIキーエラー

```txt
ValueError: GOOGLE_API_KEYが設定されていません
```

**解決方法**: `.env`ファイルにAPIキーを設定

```bash
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

#### 2. モジュールインポートエラー

```txt
ModuleNotFoundError: No module named 'src'
```

**解決方法**: Pythonパスを設定

```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

#### 3. 非同期テストの失敗

```txt
RuntimeError: Event loop is closed
```

**解決方法**: `pytest-asyncio`を使用し、`@pytest.mark.asyncio`デコレータを付与

#### 4. タイムアウトエラー

**解決方法**: タイムアウト時間を調整

```python
@pytest.mark.timeout(30)  # 30秒のタイムアウト
async def test_long_running_process():
    ...
```

## 参考資料

- [Google ADK ドキュメント](https://cloud.google.com/products/agent-development-kit)
- [Python 非同期プログラミング](https://docs.python.org/ja/3/library/asyncio.html)
- [Pytest ドキュメント](https://docs.pytest.org/)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)

## コントリビューション

プロジェクトへの貢献は歓迎します。以下の手順に従ってください：

1. このリポジトリをフォーク
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'すごい機能を追加'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## お問い合わせ

問題や質問がある場合は、Issueを作成してください。
