# 現行アーキテクチャ：Google Sheets APIベースの価格分析

## データフロー

```text
非公開Googleスプレッドシート（編集者のみが入力）
   ├── 価格履歴 A:D
   └── 商品マスタ A:B
        │ API v4 values.batchGet（1回・読み取り専用）
        ▼
Google ADC / spreadsheets.readonly（サービスアカウントを閲覧者として共有）
        ▼
src/price_viewer/sheets.py（認証・API・値→DataFrame）
        ▼
src/price_viewer/validation.py（日本円、型、欠損、重複、行番号）
        ▼
src/price_viewer/analysis.py（前回比・期間変化率）
        ▼
src/price_viewer/charts.py（Plotly）
       ├── src/price_viewer/app.py（Streamlitローカル画面・300秒キャッシュ）
       └── scripts/analyze_sheet.py（ローカルHTML/CSV）
```

`src/price_viewer/demo_data.py`は同じ入力規約を使う**架空のインメモリデータ**を提供する。CI/testsはGoogleにアクセスしない。`GOOGLE_SHEET_ID` は環境変数、認証はADC（サービスアカウントJSONをGitに置かない）。UIは現段階で`127.0.0.1`にのみバインドする。

## 料金とセキュリティ

- 1回の分析は基本的に1回のbatchGet。HTTP 429/一時的5xxのみ2回までバックオフ。無限リトライ・自動ポーリングをしない。
- Sheets API標準枠は追加料金なしだが、2026年後半に標準枠超過課金予定。Google Cloudの他製品費用は別。参照：`GOOGLE_SHEETS_SETUP.md`。
- 開発中はCloud Billing未接続・料金警戒を推奨。実運用・公開Webサービス化の前に認証、クォータ、課金上限を再審査。
- 公開リポジトリには価格の実データ・Google秘密鍵・シートIDを残さない。過去のGit履歴にあったExcelは単にファイル削除しただけでは消えない。

## 次段階で検討

店舗、価格種別、型番、出典、過去履歴、為替などを追加して複数業者の同日観測を行う。追加時はデータ契約・テスト・API範囲・入力量を別PRでレビュー。将来の中国景気推定モデルは独立した分析モジュールとして構築する。
