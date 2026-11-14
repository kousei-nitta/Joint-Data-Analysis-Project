# 現在地 / セッション引き継ぎ

更新：2026-11-14

## この移行PRで実施したこと

- 前回のExcel価格分析PR #3がmainにマージされていることを確認。
- Google Sheets API（非公開・読み取り専用）からの取得に変更。シートタブは`価格履歴`と`商品マスタ`。値の検証・グラフ化は前回実装を再利用。
- `product_prices.xlsx` を**今後のGit追跡対象から除外**。以前のGit履歴に存在するため、過去のファイルが機微情報なら履歴削除は**別途相談・承認**が必要。
- `GOOGLE_APPLICATION_CREDENTIALS` / `GOOGLE_SHEET_ID` のローカル設定とWindows/macOSの操作手順を整備。
- データ入力担当者はGoogleシートを編集するだけ。Git pushは不要。CIのGoogle認証は設けず、モック・架空データでテスト。
- Google Sheets API標準枠は現在追加料金なし。ただし2026年後半以降の枠超過課金予定があるため、永続無料ではない。

## 次の人間の承認ゲート

- このPRのコード差分、CI、旧Excel追跡解除、認証・費用方針をレビュー。mainへのマージは人間のみ。
- [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)の手順に従い人間がGoogle Cloudプロジェクト/API/サービスアカウント/プライベートシートを作成し、シートへの共有設定を行う。JSONキーはリポジトリ外で管理。
- 実シートとの接続テストは人間による認証設定後に実施し、エラー時は**JSON・ID・実データをPRに貼らず**症状のみ共有。

## まだしていないこと

- 実際の非公開シートからの読み取り検証（ユーザーのGoogle側設定が必要）。
- 店舗別・商品状態別の拡張、中国景気指標としての妥当性検証、モデル学習。
- 過去Git履歴のデータ完全削除。Cloud Billing利用・対外公開。

依頼が別AIに引き継がれる場合、`AGENTS.md`、本書、`DATA_CONTRACT.md`、`GOOGLE_SHEETS_SETUP.md`、CI結果と対象PRを読む。
