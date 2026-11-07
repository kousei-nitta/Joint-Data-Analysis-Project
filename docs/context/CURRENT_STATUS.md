# Current status / チェックポイント

更新日：2026-11-07
対象：`feat/excel-price-analysis-mvp` **レビュー待ちブランチ**（`main`にはユーザー承認後に反映）。

## 変更内容（このブランチ）

- 元Excel `product_prices.xlsx` は未変更。別の入力担当者が実データを更新してpushする予定。
- 2シート読み込み、行番号付きの入力検証、日付順の価格変化率と期間集計を実装。
- メモリ内の架空Excel（3商品・各5件）から、HTMLグラフ/CSVを生成するデモCLI、入力済みExcelのバッチ処理CLIとStreamlit画面を追加。
- テスト（データ読込・入力異常・グラフ・UIスモーク）を追加、CIにpytestとデモ生成を組み込む。
- 金額は日本円。Mac/Windows別ガイドとPDCA型の承認ゲートを追加。

## 検証の状態

- ローカル：pandas/openpyxl/Plotly/pytestを使い架空データの読込・集計・HTML/CSVをテスト。
- LinuxローカルのPythonは3.13で、正式指定の3.12.11/uv環境とは異なる。StreamlitとRuffもローカルにはないため、**GitHub Actionsの実行結果で確認が必要**。合格したチェックのみPR本文に記録する。
- 実Excelのデータ行と現行仕様の照合は未実施。既存Excelのシート名/列は `docs/plan.md` の記述に依拠する。

## 次に必要な人間の承認（Gate 2）

- PRの差分・デモ・CIの検証と、JPY前提・重複/0円エラーの仕様をレビューする。
- よければユーザー自身がmainにマージする。AIはmergeしない。

## Excel入力担当者のpush後（Gate 3、別タスク）

- 作業を開始する時点のmainの最新版を再確認し、入力済みExcelの実際のシート構造と型を検証。
- 必要な列追加や値の修正を推測で行わず、別ブランチ・PRで提案する。
- その後、精度・相関・中国景気との先行性の研究に拡張する。

別AIへの引き継ぎは `HANDOFF_TEMPLATE.md` と `LOOP_ENGINEERING.md` を使う。
