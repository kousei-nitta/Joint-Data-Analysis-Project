# 現在地：Google Sheetsのキーレス認証方針（PRレビュー前）

更新日：2026-11-14／ブランチ `chore/keyless-google-auth`

## 現状
- Google Sheets API移行PR #5はmainへマージ済み。Excelではなく非公開Googleシートを正本にする。
- 旧認証手順ではサービスアカウント秘密鍵JSONを推奨していたが、増員・将来の本番運用を考慮し**キーレスADC**に変更する。
- 人間の各PCではGoogle Cloud CLI + 個人アカウントによるSAなりすまし（短期トークン）。管理者はSheets APIとIAM Service Account Credentials APIを有効化し、SA単位でToken Creatorを付与。シート側はSAを閲覧者とする。
- コードは長期JSON秘密鍵によるADCを拒否し、トークン更新失敗時に原因を案内する。スコープは引き続き`spreadsheets.readonly`。
- Windows/macOS別の手順と将来のCloud実行SA / WIF方針は`docs/context/KEYLESS_AUTH.md`、`OS_SETUP.md`。

## 人間が確認・承認すること
1. 対象PRの変更・自動テスト・ドキュメントをレビューし、問題なければmainへマージ。
2. Google CloudのIAM Credentials APIを有効化、開発者ごとに特定SAのToken Creatorを付与。鍵JSONは発行しない。
3. 開発者本人のPCで`gcloud auth application-default login --impersonate-service-account=...`後、非公開シートの実データ取得を確認する（実データはPRに掲載しない）。

## 未実施
- Google CloudのIAM設定・Cloud Billing操作・実シートの認証付き疎通テスト。
- 自動公開・課金設定・LLMによる経済予測。

詳細はADR0005、`AGENTS.md`、`docs/context/KEYLESS_AUTH.md`。
