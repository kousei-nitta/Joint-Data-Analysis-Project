# Joint-Data-Analysis-Project

**Excelに手入力した商品価格をPythonで検証・分析し、日付別の価格推移をグラフにするローカルデモ**です。現段階では中国景気の予測AIではありません。分析ロジックは将来的なオルタナティブ指標研究の基盤になります。

## 今すぐ試す

`uv` 0.13.5 と Python 3.12.11 を使用します。Windows と macOS の詳しい手順は [OS別セットアップ](docs/context/OS_SETUP.md) を参照してください。

```bash
uv python install 3.12.11
uv sync --locked
uv run --locked python scripts/run_demo.py
uv run --locked streamlit run src/price_viewer/app.py
```

実データを画面なしでグラフ・CSVに変換する場合（Excelが入力済みの場合のみ）：

```bash
uv run --locked python scripts/analyze_workbook.py --excel product_prices.xlsx
```

`http://127.0.0.1:8501` を開くと、まず**架空データ**の価格推移グラフが表示されます。データ入力担当者のExcel完成後には「Excelをアップロード」または「リポジトリのExcel」から読み込めます。xlsx原本への書き込みは行いません。

## できること

- `product_prices.xlsx` の「価格履歴」「商品マスタ」の2シートを読み取り、商品IDを文字列のまま照合。
- 空行の無視、欠落・不正日付・不正価格・未登録商品ID・重複の**行番号付き**エラー表示。
- 商品と期間の選択、観測価格の折れ線グラフ、前回比（円・%）と期間の変化率。
- グラフをHTML、分析データをCSVとしてローカル保存。`outputs/` はGit追跡外。
- CIで架空のExcelから分析結果までをテスト。実在の商品・取引価格はテストに使用しません。

## 試験運用の制約

- 金額は当面**日本円（JPY）**。税の扱い、商品状態、店舗の識別は現在のExcel列に存在せず未確定。
- 同一商品ID・同じ日の複数レコードは店舗差を識別できないためエラー。勝手な平均・値の補完をしません。
- デモは架空データであり、中国景気との因果性・先行指標としての精度は未検証。
- 新しい商品価格がGitHubにpushされた後、**別PRで実Excelとの整合性を確認する**予定です。

## 開発・テスト

```bash
uv run --locked python scripts/check_environment.py
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

対象コード: `src/price_viewer/`、出力デモ: `scripts/run_demo.py`、テスト: `tests/`。既存の `product_prices.xlsx` は更新しません。

## AIと人間が共通の設計履歴を使う

まず [AGENTS.md](AGENTS.md) を読み、[共有設計](docs/context/ARCHITECTURE.md)、[Excelデータ契約](docs/context/DATA_CONTRACT.md)、[分析MVP仕様](docs/context/ANALYSIS_MVP_SPEC.md) を参照してください。[反復開発と承認ゲート](docs/context/LOOP_ENGINEERING.md)、[現在地](docs/context/CURRENT_STATUS.md)、[作業引き継ぎ](docs/context/HANDOFF_TEMPLATE.md)、[判断の履歴](docs/adr/) によって、ChatGPT・Claude・ローカルLLMに依存せず作業を引き継げます。[貢献ガイド](CONTRIBUTING.md) も参照してください。
