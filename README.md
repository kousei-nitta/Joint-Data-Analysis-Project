# Joint-Data-Analysis-Project

Excelに記録した商品価格を読み込み、ブラウザで価格推移を確認する試作品です。
**現在は開発基盤の準備段階です。価格分析アプリ本体はまだ実装していません。**

## 使用するもの

| 用途 | 採用 |
| --- | --- |
| Python | 3.12.11（既存のpyenvを利用） |
| 仮想環境・依存関係管理 | uv 0.13.5、`.venv`、`uv.lock` |
| Excel読み込み・加工 | pandas、openpyxl |
| ブラウザ画面・操作できるグラフ | Streamlit、Plotly |
| 開発チェック | Ruff、pytest（アプリ実装時にテストを追加） |

## macOSで準備

Python 3.12.11がpyenvにインストール済みであることを前提にします。
uv未導入の場合は `brew install uv`（このリポジトリで使う版は0.13.5）。
Homebrewの提供版が異なる場合は[uv公式のバージョン指定インストール](https://docs.astral.sh/uv/getting-started/installation/)を利用してください。

```bash
cd /Users/kousei/Joint-Data-Analysis-Project
uv sync --locked --python "$(pyenv root)/versions/3.12.11/bin/python"
uv run --locked python scripts/check_environment.py
```

他の人はcloneしたフォルダへ移動してください。`uv sync`が`.venv`を作成し、
固定済みのライブラリをインストールします。`uv run`を使えば毎回の有効化は不要です。
エディタのPythonは `.venv/bin/python` を選びます。

## ブラウザ表示だけ試す

```bash
uv run --locked streamlit hello
```

これはStreamlit付属のデモです。`http://127.0.0.1:8501` で開き、終了は `Ctrl+C`。
価格分析アプリの起動コマンドは、アプリ実装時に追加します。

## フォルダ構成

```text
product_prices.xlsx       # 既存の共有Excel。位置・内容は維持
src/price_viewer/         # 次の段階でアプリ本体を配置
tests/                    # 次の段階でアプリのテストを配置
scripts/                  # 開発環境の確認
data/local/               # 個人用Excelのコピーなど（Git管理外）
outputs/                  # 生成するグラフ等（Git管理外）
docs/plan.md              # 設計案・入力仕様・次の実装範囲
.github/                  # PRテンプレート・自動チェック
pyproject.toml / uv.lock  # 必要ライブラリ・固定されたバージョン
```

入力は当面`.xlsx`を使います。複数シート、入力規則、商品マスタを保持できるためです。
CSVは今後の外部連携・出力が必要になった段階で追加します。

開発の進め方は [CONTRIBUTING.md](CONTRIBUTING.md)、
実装前に確認する内容は [docs/plan.md](docs/plan.md) を参照してください。
