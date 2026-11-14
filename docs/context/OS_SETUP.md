# ローカル手順：Windows（PowerShell） / macOS（zsh）

共通：GitHubで管理するのはPythonコードと設計書だけ。価格の入力は権限が付いた**非公開Googleスプレッドシート**で行う。初期設定と料金説明は [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)。Python `3.12.11` / uv `0.13.5`を使用。

## Windows（PowerShell）

```powershell
# clone済みリポジトリで実行。実際の保存先に合わせて修正
Set-Location "$HOME\Documents\Joint-Data-Analysis-Project"
git switch main
git pull --ff-only
uv python install 3.12.11
uv sync --locked
uv run --locked pytest -q
uv run --locked python scripts/run_demo.py
```

Google Cloud CLIを[公式手順](https://cloud.google.com/sdk/docs/install)でインストールし、各開発者本人のGoogleアカウントで以下を実行。事前に管理者がSheets API / IAM Credentials APIを有効にし、サービスアカウント単位のToken Creator権限を付与します。秘密鍵JSONは**作成しません**。

```powershell
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login --impersonate-service-account=sheet-price-reader@YOUR_PROJECT_ID.iam.gserviceaccount.com
$env:GOOGLE_SHEET_ID = "スプレッドシートURLのID部分"
uv run --locked python scripts/analyze_sheet.py
uv run --locked streamlit run src/price_viewer/app.py
```

ブラウザ `http://127.0.0.1:8501` →「非公開Googleスプレッドシート」を選択。次回新しいPowerShellを開いた場合は `GOOGLE_SHEET_ID` を再設定してください。**Google認証の秘密鍵JSONを使用したり、環境変数に鍵ファイルのパスを設定したりする必要はありません。** ADCのログイン情報はローカルのGoogle Cloud CLI管理場所へ保存されます。

VS Codeインタープリター：`.venv\Scripts\python.exe`（Ctrl+Shift+P → Python: Select Interpreter）。

## macOS（ターミナル / zsh）

```bash
# clone済みリポジトリで実行。実際の保存先に合わせて修正
cd ~/Joint-Data-Analysis-Project
git switch main
git pull --ff-only
uv python install 3.12.11
uv sync --locked
uv run --locked pytest -q
uv run --locked python scripts/run_demo.py
```

Google Cloud CLIを[公式手順](https://cloud.google.com/sdk/docs/install)でインストールし、各開発者本人のGoogleアカウントで以下を実行。事前に管理者がSheets API / IAM Credentials APIを有効にし、サービスアカウント単位のToken Creator権限を付与します。

```bash
unset GOOGLE_APPLICATION_CREDENTIALS
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login --impersonate-service-account=sheet-price-reader@YOUR_PROJECT_ID.iam.gserviceaccount.com
export GOOGLE_SHEET_ID="スプレッドシートURLのID部分"
uv run --locked python scripts/analyze_sheet.py
uv run --locked streamlit run src/price_viewer/app.py
```

VS Codeインタープリター：`.venv/bin/python`（Cmd+Shift+P → Python: Select Interpreter）。別ターミナルではexportを再実行してください。

## 共通の操作とトラブル

- `uv run --locked python scripts/run_demo.py` は**Googleへのアクセスなし**に架空データのHTML/CSVを作成します。
- `uv run --locked python scripts/analyze_sheet.py` は非公開シートを読み取り、`outputs/analysis/` に商品別HTML/CSVを保存します。
- Streamlitはデフォルトで架空デモ。実データを見たいときだけ入力元を切替。シートの変更から画面への反映は最大5分程度（「最新のデータを再取得」で即時更新）。
- 商品IDはSheetsの列を「書式なしテキスト」にして入力し、`001`を保持。価格は数値、日本円で記録。確認日は有効な日付。
- 長期鍵JSONは作成せず、ローカルADCファイルやトークンを他人に送らず、GitHub・PR・Issueに添付しない。サービスアカウントには**閲覧者**権限のみ与えます。
- 403は権限、404はID/共有状態、400はタブ名、入力エラーは指定した行/列を確認。Pythonやuvが認識されない場合は個別インストールを確認。
