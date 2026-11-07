# アーキテクチャ：現状と目標を分ける

## AS-IS（2026-11-07時点のリポジトリ確認）
- `product_prices.xlsx`：既存入力テンプレート。
- `scripts/check_environment.py`：メモリ上で生成したExcelからの読込、商品ID、Plotly HTML出力の動作検査。
- `pyproject.toml` / `uv.lock`：Python 3.12.11、uv 0.13.5、pandas、openpyxl、Plotly、Streamlit等の依存関係。
- `.github/workflows/ci.yml`：環境・Ruffチェック。
- `src/price_viewer/` と `tests/`：プレースホルダー。**分析機能・本番UI・自動収集は未実装**。

## TO-BE（次のPR以降に段階的に実装する想定）
```text
Excel（読み取り専用）/ 許諾済みデータ
          |
          v
read_excel -> validate -> normalize -> analyze -> plot/report
                 |                    |
                 +--> 例外・行番号      +--> PNG/HTML/CSV（outputs/, Git管理外）
                           |
                       （任意）Streamlit ローカルUI
```

推奨する責務分割（**ディレクトリ案であり現存実装ではない**）：
- `src/price_viewer/io.py`：Excelシート読込。入力ブックを保存しない。
- `src/price_viewer/validation.py`：必須列、日付、金額、ID、重複の検査。
- `src/price_viewer/analysis.py`：前回比、期間変化率、欠損管理。
- `src/price_viewer/charts.py`：グラフ/レポート生成。
- `src/price_viewer/app.py`：任意のStreamlit表示。業務ロジックを置かない。
- `tests/`：openpyxlで作る架空データと期待値による単体テスト。

## データ境界
- Excelは入力の正本。原本の上書き禁止。変換後のDataFrameは派生データ。
- `data/local/`：個人のコピー、`outputs/`：生成物。いずれも原則Git追跡外。
- データ取得元のライセンス・商用利用条件・証拠を記録してから収集処理を追加する。
- 外部API・LLMによる文章生成は後段の任意機能。数値の計算・検証は再現可能なPythonの処理に置く。

## 実装順
1. `docs/context/DATA_CONTRACT.md` に沿った読込と検証。
2. ダミーデータの正常系・異常系テスト。
3. 価格変化率と折れ線グラフ。ゼロ割り・欠損・重複の取り扱いを明示する。
4. ローカルUIまたは記事用出力（目的に応じて選択）。
5. データ量と観測期間が整ってから異常検知・先行性の統計検証を設計する。

## 品質上の制約
価格の下落は中国景気悪化の証明ではない。為替、世界相場、新機種発売、状態差、店舗在庫、掲載価格と成約価格の違いなどを取り除く必要がある。複数商品の重み付けや独自指数は未設計。
