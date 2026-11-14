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

Google Cloudで作成した**秘密鍵JSONはリポジトリの外**、例えば `$HOME\private-keys\price-reader.json` に保存します。実際のパスとシートIDへ置き換えて、**このPowerShell画面だけ**に環境変数を設定します：

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "$HOME\private-keys\price-reader.json"
$env:GOOGLE_SHEET_ID = "スプレッドシートURLのID部分"
uv run --locked python scripts/analyze_sheet.py
uv run --locked streamlit run src/price_viewer/app.py
```

ブラウザ `http://127.0.0.1:8501` →「非公開Googleスプレッドシート」を選択。次回新しいPowerShellを開いた場合は環境変数を再設定してください。永久環境変数に秘密鍵そのものを入れず、**ファイルへのパス**を指定します。

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

認証JSONをリポジトリ**外**のフォルダに保存します。例：`$HOME/private-keys/price-reader.json`。実際のパスとIDへ置き換える：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/private-keys/price-reader.json"
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
- 認証JSONや秘密情報を他人に送らず、GitHub・PR・Issueに添付しない。サービスアカウントには**閲覧者**権限のみ与えます。
- 403は権限、404はID/共有状態、400はタブ名、入力エラーは指定した行/列を確認。Pythonやuvが認識されない場合は個別インストールを確認。
