# ADR 0004: 非公開Googleスプレッドシートを価格データの正本にする

- Status: Accepted（Google Sheets正本を採用）。認証JSONの部分はADR0005によって置換予定
- Date: 2026-11-14

## Context

ExcelをGitに入れると入力担当者が小さな変更のたびにpushする手間があり、バイナリ差分も管理しづらい。チームのMac/Windowsで同時編集をしたい。一方Google Sheets APIには現在無料の標準利用枠があるが、超過料金は2026年後半に導入予定と案内されている。

## Decision

- データの正本をGoogleスプレッドシートに移す。人間は指定した編集権限で共同入力。
- PythonはGoogle Sheets APIの`values.batchGet`を**読み取り専用**で使用。サービスアカウントに閲覧権限を与え、ADCを用いる。
- `GOOGLE_SHEET_ID`と認証JSONをGitに載せない。旧Excelを最新ブランチから除外する。
- ローカルアプリのキャッシュは5分、強制更新ボタン、レート制限時の最大2回のバックオフを採用。
- 機能テスト・CIは架空データを用い、Google Cloud課金やネット接続に依存しない。

## Consequences

- 開発者によるデータpushは不要。履歴と共同編集はGoogle Sheetsに委ねる。
- API認証の初回セットアップとクラウドサービスの長期的な運用監視が発生。
- 人間が編集者、プログラムは閲覧者という最小権限分離ができる。
- 既存ADR 0002/0003の**「Excel原本の運用」はこのADRにより将来分が置き換えられる**。既存の歴史的決定は削除しない。
- Git履歴に含まれる古いExcelは別途履歴操作がなければ残る。

## Alternative

Excel+Git継続、ローカルDB、Google Sheets CSV公開URL、Google Apps Script API。特に公開CSVは非公開要件を満たさないため不採用。
