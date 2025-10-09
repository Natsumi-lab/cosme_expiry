# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

このプロジェクトは、化粧品やメイク用品の **使用期限を管理するアプリ** です。  
ユーザーは商品名・開封日・カテゴリ・形状などを登録することで、自動的に使用期限を計算・通知を受け取れます。  
また、LLM（ChatGPT API）を利用してカテゴリや形状を自動補完し、衛生リスクや使用ペース改善のアドバイスを提示します。  
ポートフォリオとして、実務で使える設計力・実装力・デザイン力をアピールする目的も含みます。

## 開発用コマンド

### Django管理コマンド

```bash
# 開発サーバー起動
python manage.py runserver

# データベース操作
python manage.py makemigrations
python manage.py migrate

# 管理画面操作
python manage.py createsuperuser

# テストとメンテナンス
python manage.py check
python manage.py test
python manage.py shell

# 静的ファイル（必要な場合）
python manage.py collectstatic
```

### データベース管理

```bash
# マイグレーション状況の確認
python manage.py showmigrations

# 特定アプリのマイグレーション作成
python manage.py makemigrations beauty

# 特定マイグレーションの適用
python manage.py migrate beauty
```

## プロジェクト構成

### Django構造

単一アプリケーション構成のDjangoプロジェクトです：

- **メインプロジェクト**: `cosme_expiry_app/` - 設定、メインURL、WSGI/ASGI設定を含む
- **Beautyアプリ**: `beauty/` - すべてのビジネスロジックを含むメインアプリケーション
  - **モデル**: `Taxon`（階層カテゴリ）、`Item`、`Notification`、`LlmSuggestionLog`を含む包括的なモデル構造
  - **ビュー**: 基本的なホームビューとLLM統合機能（`views.py`）
  - **管理画面**: すべてのモデルに対してカスタムフィルタと表示オプションを持つ完全に設定された管理インターフェース
  - **フォーム**: 最小限のフォーム構造（`forms.py`）
  - **テンプレート**: `base.html`と`home.html`によるBootstrapベースのレスポンシブデザイン
  - **静的ファイル**: 分離されたCSS（`styles.css`、`custom-styles.css`）とJavaScript（`scripts.js`）

### 主要設定

- **言語**: 日本語（`ja`）、アジア/東京タイムゾーン
- **データベース**: 開発用SQLite
- **デバッグモード**: 開発用に有効
- **静的ファイル**: `beauty/static/`ディレクトリで設定
- **テンプレート**: `beauty/templates/`に配置
- **仮想環境**: `venv/`ディレクトリを使用（他のプロジェクトの`myenv/`ではない）

### 現在の実装状況

**実装済み機能:**
- **データモデル**: Taxon（階層カテゴリ）、Item、Notification、LLM提案ログを含む完全なモデル構造
- **管理インターフェース**: カスタムフィルタ、検索、表示オプションを持つ完全に機能する管理画面
- **LLM統合フレームワーク**: views.pyでのChatGPT API統合の基本構造
- **フロントエンドテンプレート**: モバイルサポート付きレスポンシブBootstrapデザイン

**実装予定機能:**
- **アイテム管理**: 化粧品アイテムのCRUD操作（モデルは存在、ビューが必要）
- **通知システム**: 自動期限切れ通知（モデルは存在、スケジューリングロジックが必要）
- **完全なLLM統合**: OpenAI API接続とカテゴリ自動補完
- **ユーザー認証**: フロントエンドログイン/登録（Django認証は設定済み）
- **統計ダッシュボード**: カテゴリ分布と期限状況を示すグラフ
- **検索とフィルタリング**: 高度なアイテムフィルタリング機能

## ファイル組織基準

### テンプレート構造

- `base.html`: レスポンシブナビバー、モバイルメニュー、フッターを持つメインテンプレート
- Bootstrap 5.2.3とFont Awesomeアイコンを使用
- 統計表示用のChart.js統合
- 複数ファイルに分離されたカスタムCSS

### 静的ファイル組織

```
beauty/static/
├── css/
│   ├── styles.css          # メインスタイル
│   └── custom-styles.css   # カスタムオーバーライド
├── images/
│   ├── favicon.ico
│   └── header.jpg
└── js/
    └── scripts.js          # メインJavaScript
```

### コーディング規約

- **ファイル分離**: HTML、CSS、JavaScriptは必ず別ファイルに分ける
- **インラインスタイル禁止**: すべてのスタイリングはCSSファイルで行う
- **インラインスクリプト禁止**: すべてのJavaScriptは別ファイルで行う
- **レスポンシブデザイン**: Bootstrapでモバイルファーストアプローチ
- **アクセシビリティ**: 適切なARIAラベルとセマンティックHTML

## デザインシステム

### カラーパレット

- プライマリ: `#f8dec6`（ライトクリーム）
- セカンダリ: `#c7b19c`（ウォームブラウン）
- アクセント: `#d3859c`（ダスティローズ）
- テキスト: `#000000`（ブラック）

### デザイン方針

- モダンで洗練された都市的スタイル
- クリーンでミニマルなインターフェース
- 使いやすさとアクセシビリティに重点

## 開発環境

- **Python**: 3.13.5
- **Django**: 5.2.4（pip listで確認済み）
- **フロントエンド**: Bootstrap 5.2.3、Font Awesome 6.0.0、Chart.js
- **データベース**: SQLite（開発用）
- **仮想環境**: `venv/`（Windowsでは`venv\Scripts\activate`で有効化）

### 仮想環境管理

```bash
# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 依存関係のインストール（requirements.txtはまだ存在しない）
pip install Django==5.2.4

# パッケージインストール後の要件ファイル生成
pip freeze > requirements.txt
```

## デプロイ設定

- **対象プラットフォーム**: PythonAnywhere
- **外部API**: LLM機能用のOpenAI API
- **画像ストレージ**: 最初はローカルストレージ、後にクラウドストレージ（S3/Cloudinary）を予定
- **セキュリティ**: 開発用シークレットキーが存在（本番用に変更が必要）

## モデル構成詳細

### Taxonモデル（階層カテゴリ）
- 化粧品カテゴリのツリー構造を実装（例：メイクアップ > リップ > リップグロス）
- 保存時にdepthとfull_pathを自動計算
- 管理画面でItem.product_typeを葉ノードのみに制限
- 主要メソッド: 子カテゴリの有無をチェックする`is_leaf`プロパティ

### Itemモデル（メインエンティティ）
- ForeignKeyでUserにリンク
- 階層カテゴリ化にTaxonを使用
- 期限計算フィールド（`opened_on`、`expires_on`、`expires_overridden`）を含む
- ステータス追跡：'using'または'finished'
- リスク評価：期限アラート用の'low'、'mid'、'high'
- プロパティ：階層ナビゲーション用の`main_category`、`middle_category`

### LLM統合構造
- `LlmSuggestionLog`がAI提案とユーザー選択を追跡
- カテゴリ、商品名、ブランド提案をサポート
- 学習用に提案されたtaxonと選択されたtaxonの両方を記録

## 開発メモ

- マイグレーション適用済みの完全なモデル構造が実装済み
- すべてのモデルに対して管理インターフェースが完全に設定済み
- 認証システムは設定済みだがフロントエンドは未実装
- LLM統合フレームワークは設置済み、API接続が必要
- グラフと統計機能はテンプレート化済みだがバックエンドビューが必要
- モバイルレスポンシブはテンプレートで完全実装済み
- requirements.txtファイルなし - 依存関係の文書化が必要