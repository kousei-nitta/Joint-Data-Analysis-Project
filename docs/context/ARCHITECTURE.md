# アーキテクチャ（設計と実装状況）

## 今回の分析MVPブランチ（未マージ）

```text
実Excelまたは架空Excel（既存2シート）
                |
      io.load_price_workbook
                |
    validation.validate_frames --> 入力エラー（行番号・列名）
                |
    DataFrame（date, product_id, product_name, price_jpy, note, excel_row）
                |
      analysis.py（期間、前回比、サマリー）
                |
        charts.py（Plotlyグラフ）
              /   \
    Streamlit UI   HTML/CSV（ローカル）
```

## ファイル責務

- `product_prices.xlsx`：入力担当が更新する既存テンプレート。分析コードは読み取り専用。
- `src/price_viewer/io.py`：ファイル検査、シート読込。
- `src/price_viewer/validation.py`：日付・商品ID・価格・重複などを検証し、元Excel行番号付きの問題を返す。
- `src/price_viewer/analysis.py`：観測値の変化率、期間で絞り込んだ統計量。
- `src/price_viewer/charts.py`：Plotlyグラフの構築。
- `src/price_viewer/demo_data.py`：**架空データのみ**のメモリ内Excel生成。
- `src/price_viewer/app.py`：ローカルStreamlit UI。数値計算ロジックを持たない。
- `scripts/run_demo.py`：架空Excel→HTML/CSVのCLI動作確認。
- `scripts/analyze_workbook.py`：入力済みExcelから商品別HTML/CSVを出力するバッチ処理（ファイル名は商品IDのハッシュで安全化）。
- `tests/`：データ契約、演算、グラフ、UIスモークテスト。
- `data/local/`、`outputs/`：Git追跡外。実データや成果物を公開コミットしない。

## スコープ外

データベース、スクレイパー、中国の景気予測モデル、為替補正、店舗比較、認証・一般公開、商用配信は未実装。先行性の研究は入力データの信頼性を確保してから着手する。

## OSと再現性

Python 3.12.11 / uv 0.13.5 / `uv.lock` が前提。画面は127.0.0.1ローカル起動。Mac/Windowsの具体的な操作は `OS_SETUP.md`。AI間共有の運用ルールは `AGENTS.md` と `LOOP_ENGINEERING.md`。
