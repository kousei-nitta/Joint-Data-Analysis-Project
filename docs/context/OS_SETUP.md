# ローカル実行手順：Windows / macOS

前提：リポジトリをclone済み、VS Code・Git・uv **0.13.5**、Python **3.12.11**を使う。`pyproject.toml` のバージョン固定と `uv.lock` を守る。コマンドは**リポジトリ直下**で実行。Excel原本 `product_prices.xlsx` は更新しない。

## Windows（PowerShell）

```powershell
# 例：自分のclone先へ移動。PCに合わせて変更してください。
Set-Location "$HOME\Documents\Joint-Data-Analysis-Project"
uv --version
uv python install 3.12.11
uv sync --locked
uv run --locked python scripts/check_environment.py
uv run --locked pytest -q
```

デモグラフと数表だけ保存する：

```powershell
uv run --locked python scripts/run_demo.py
# 保存先: outputs\demo\demo_001.html など（架空データ）
```

ブラウザで商品と期間を切り替える：

```powershell
uv run --locked streamlit run src/price_viewer/app.py
# ブラウザ: http://127.0.0.1:8501
# 終了: ターミナルで Ctrl+C
```

VS CodeのPythonインタープリターは `.venv\Scripts\python.exe` を選ぶ（`Ctrl+Shift+P` → Python: Select Interpreter）。PowerShellで仮想環境を有効化する必要はなく `uv run` で実行可能。

## macOS（ターミナル / zsh）

```bash
# 例：自分のclone先へ移動。PCに合わせて変更してください。
cd ~/Joint-Data-Analysis-Project
uv --version
uv python install 3.12.11
uv sync --locked
uv run --locked python scripts/check_environment.py
uv run --locked pytest -q
```

既にpyenv管理の3.12.11を使っていて統一したい場合は、`uv sync --locked --python "$(pyenv root)/versions/3.12.11/bin/python"` も使用可能。uv管理のPythonを使うならpyenvは必須ではない。

デモグラフと数表だけ保存する：

```bash
uv run --locked python scripts/run_demo.py
# 保存先: outputs/demo/demo_001.html など（架空データ）
```

ブラウザで商品と期間を切り替える：

```bash
uv run --locked streamlit run src/price_viewer/app.py
# ブラウザ: http://127.0.0.1:8501
# 終了: Ctrl+C
```

VS CodeのPythonインタープリターは `.venv/bin/python` を選ぶ（`Cmd+Shift+P` → Python: Select Interpreter）。

## Excel入力が完了した後のバッチ分析

Windows（PowerShell）：

```powershell
uv run --locked python scripts/analyze_workbook.py --excel product_prices.xlsx
# outputs\analysis\ にHTMLとCSVが保存される
```

macOS（zsh）：

```bash
uv run --locked python scripts/analyze_workbook.py --excel product_prices.xlsx
# outputs/analysis/ にHTMLとCSVが保存される
```

Excelが未入力または不正な場合は、修正対象の行番号と列名が表示され、結果は作成されない。

## 共通の画面操作

1. 最初は「**架空デモデータ**」を選択。3商品の仮データをグラフ化できる。
2. 「**Excelをアップロード**」で、入力担当者が完成させた `.xlsx` ファイルを選択できる。ファイルは読み取り専用。
3. 「**リポジトリのExcel**」はローカルの `product_prices.xlsx` を読む。未入力の場合はエラー案内が表示される。原本への書き込みはしない。
4. 商品・期間を選ぶと、観測データ・前回比・期間変化率・Plotlyグラフが変わる。
5. HTML（オフライン閲覧可能）とCSVを保存できる。公開前に出典・再利用条件を確認。

## よくある問題

- `uv` コマンドが見つからない：OS別のuvインストール手順を確認。必要版は `0.13.5`。
- 別Pythonが選択される：`uv run --locked python --version` で3.12.11を確認。VS Codeの環境選択は上記。
- Excelが分析できない：画面にシート名・行番号・列名が表示される。`docs/context/DATA_CONTRACT.md` を確認。
- 同じ日に同一商品IDの価格が複数：現行テンプレートに店舗列がないため区別不可。勝手な平均は行わず入力を修正するか、別PRで仕様を拡張。
- 無料のローカル表示が目的：外部公開やネットワーク接続は不要。`localhost` の画面を共有する場合は情報管理に注意。
