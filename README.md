# Joint-Data-Analysis-Project

非公開の**Googleスプレッドシート**で価格データを共同編集し、Pythonが **Google Sheets API（読み取り専用）** から取得して、商品価格の推移グラフ・CSV・HTMLを生成します。入力データをGitHubへpushする必要はありません。

> 現時点で提供するのは**価格推移の分析**です。中国景気や不動産バブルの予測AIの有効性はまだ検証していません。

## データ管理の原則

- データの正本は**閲覧・編集権限を指定したGoogleスプレッドシート**です。コードだけGitHubで管理します。
- Googleシートの「価格履歴」（`確認日, 商品ID, 価格, 備考`）と「商品マスタ」（`商品ID, 商品名`）の列構成を維持します。**商品IDは文字列**（例：`001`）、価格は数値の**日本円**、確認日は日付で入力してください。
- 認証はGoogleのApplication Default Credentials（ADC）を使用し、`spreadsheets.readonly` 権限のみを要求します。スプレッドシートはサービスアカウントに「閲覧者」として共有します。
- **長期サービスアカウント鍵JSONを作成・配布せず**、ローカルではGoogle Cloud CLIでキーレスADC（サービスアカウントのなりすまし）を設定します。シートID、ADCファイル、実測データをGitHubへコミットしません。出力は`outputs/`に保存され、Git管理対象外です。
- **これまで追跡していた `product_prices.xlsx` は今回の移行PRで追跡対象から削除**しています。過去のGitコミット履歴からは消えない点に注意してください。

## すぐに試す（Google認証・インターネット不要）

Python `3.12.11` と uv `0.13.5` を使用。詳細は[Windows/macOS別の操作手順](docs/context/OS_SETUP.md)。

```bash
uv python install 3.12.11
uv sync --locked
uv run --locked python scripts/run_demo.py
uv run --locked streamlit run src/price_viewer/app.py
```

画面 `http://127.0.0.1:8501` の初期選択は「架空デモデータ」です。3商品×5回の**架空価格**を分析でき、実在の取引情報は含みません。

## 非公開Googleスプレッドシートとの接続

1. [Google Cloudの初期設定](docs/context/GOOGLE_SHEETS_SETUP.md) に従い、Google Cloudプロジェクト、Google Sheets APIおよびIAM Service Account Credentials APIを用意。
2. 秘密鍵を持たないサービスアカウントを作成して、目的のGoogleスプレッドシートをそのアカウントへ**閲覧者**として共有。
3. 各開発者にサービスアカウント単位のToken Creator権限を付与し、[キーレス認証の手順](docs/context/KEYLESS_AUTH.md)でADCを設定します。
4. Streamlit画面の「非公開Googleスプレッドシート」を選ぶか、下記コマンドでHTML/CSVを出力。

```bash
uv run --locked python scripts/analyze_sheet.py
```

`GOOGLE_SHEET_ID` は共有シートのURL `https://docs.google.com/spreadsheets/d/<ここがID>/edit` のID部分です。**環境変数のみで管理**し、GitHubには書かないでください。

APIからの読み取りは一度に「価格履歴」「商品マスタ」の両シートを `values.batchGet` で取得します。Streamlitは5分間キャッシュし、手動で更新できます。日付・商品ID・価格の検証結果を確認してから分析します。シートへの書き込みはありません。

## できること

- 商品別・期間別に価格と前回比・変化率を算出し、折れ線グラフを表示。
- 日付不正・未登録ID・重複・不正価格を、Googleシートの行番号と列名で報告。空欄を勝手に0円にしません。
- CSV/HTML出力（ローカルのみ）。価格の穴埋め・為替補正・中国景気予測は未実装。
- 架空データを使ったネットワーク不要の自動テスト。CIには実際のGoogle認証情報を登録しません。

## 開発・レビュー

```bash
uv run --locked python scripts/check_environment.py
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

[キーレス認証](docs/context/KEYLESS_AUTH.md)、[AGENTS.md](AGENTS.md)、[共通のデータ契約](docs/context/DATA_CONTRACT.md)、[アーキテクチャ](docs/context/ARCHITECTURE.md)、[反復開発・承認ゲート](docs/context/LOOP_ENGINEERING.md)、[現状](docs/context/CURRENT_STATUS.md)を参照。ChatGPT・Claude・ローカルLLMのチャット履歴に依存せず作業を再開できます。
