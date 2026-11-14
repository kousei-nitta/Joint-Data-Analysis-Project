# キーレス認証の標準運用（Windows / macOS / 将来の本番環境）

更新日：2026-11-14。Google公式資料を前提とし、料金・IAM設定は実施時点に再確認する。
**チーム標準は「サービスアカウントのなりすまし（impersonation）+ Application Default Credentials（ADC）」**。Googleの長期サービスアカウント鍵JSONを作成・配布しない。

## 目的と構成
- データ入力者：権限を付与されたGoogleアカウントで**非公開**スプレッドシートを編集。Gitでデータを管理しない。
- Python開発者：各自のGoogleアカウントでGoogle Cloud CLIにログイン。専用**閲覧者サービスアカウント**の短期アクセストークンを、認可を受けた人だけが代理取得する。
- 実行中のPython：`google.auth.default(scopes=[spreadsheets.readonly])` によってADCを取得。Sheets API `values.batchGet` で読み取りのみ。Google Cloudのプロジェクト管理権限やSheets編集権限は不要。
- 共通Google認証JSON鍵をメンバー間で送らない。メンバー追加・削除はIAMの**サービスアカウント単位**の権限変更で実施できる。

```text
人間A / 人間B (各自gcloudログイン)
      |  IAM: roles/iam.serviceAccountTokenCreator (指定のSAだけ)
      v
専用SAの短期トークン（鍵JSONなし）
      |  Google Sheetsで「閲覧者」
      v
非公開シート --Sheets API readonly--> Python分析・グラフ
```

**注意：キーレスでも無認証・PCに秘密情報が残らないという意味ではありません。** Google Cloud CLIによるADCは利用者の認証情報をOS上のローカルファイルに保存します（トークン更新用資格情報を含む）。端末ロック、ディスク暗号化、OSユーザー別アカウント、退職者のアクセス取り消し、不要時の `gcloud auth application-default revoke` が必要です。生成される**サービスアカウントのアクセストークンは短期有効**です。

## 管理者が最初に一度だけ行うこと

1. [Google Cloud Console](https://console.cloud.google.com/) で専用プロジェクトを選び、**Google Sheets API** と **IAM Service Account Credentials API**（`iamcredentials.googleapis.com`）を有効化する。
2. 用途専用のサービスアカウント（例 `sheet-price-reader@PROJECT_ID.iam.gserviceaccount.com`）を作成する。**秘密鍵を生成しない。** プロジェクト全体のOwner/Editor/Viewerは付与しない。
3. Google Sheetsで「一般的なアクセス：制限付き」を維持。サービスアカウントのメールをそのシートだけの**閲覧者**に追加する。人間の編集者は別途指定する。
4. Google Cloud Console → IAMと管理 → サービスアカウント → 上記サービスアカウント → 権限（アクセスを管理）から、開発者のGoogleアカウント**各人**に `サービス アカウント トークン作成者`（`roles/iam.serviceAccountTokenCreator`）を**このサービスアカウントに限って**付与する。プロジェクトIAM全体にこのロールを付与しない。
5. 人が増えたときは新しいメンバーのアカウントだけを追加。離脱時は該当アカウントのToken Creatorとシート編集者/閲覧者権限を両方取り消す。共有アカウントは作らない。

「Token Creator」は指定サービスアカウントになりすませる強い権限です。専用SAにはこの非公開シートの閲覧だけを許可し、他のサービスの強い権限を与えないでください。IAM操作は管理者による承認ゲートです。

## 各開発者：ローカルで一度設定

Google Cloud CLIを公式インストーラーで導入：
- Windows: [Google Cloud CLIのインストール](https://cloud.google.com/sdk/docs/install) を開きWindows用インストーラーを選択し、PowerShellを再起動。
- macOS: 同じ公式ページのmacOS向け手順に従い、ターミナルを再起動。

すでに`GOOGLE_APPLICATION_CREDENTIALS`に長期キーJSONのパスが設定されている場合、**ADCはそちらを優先します**。削除または解除してください。

### Windows（PowerShell）
```powershell
# 既存のキーJSONパス指定を解除（このPowerShellセッション）
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue

gcloud --version
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login --impersonate-service-account=sheet-price-reader@YOUR_PROJECT_ID.iam.gserviceaccount.com

$env:GOOGLE_SHEET_ID = "スプレッドシートURLのID"
uv sync --locked
uv run --locked python scripts/analyze_sheet.py
uv run --locked streamlit run src/price_viewer/app.py
```

### macOS（zsh）
```bash
# 既存のキーJSONパス指定を解除
unset GOOGLE_APPLICATION_CREDENTIALS

gcloud --version
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login --impersonate-service-account=sheet-price-reader@YOUR_PROJECT_ID.iam.gserviceaccount.com

export GOOGLE_SHEET_ID="スプレッドシートURLのID"
uv sync --locked
uv run --locked python scripts/analyze_sheet.py
uv run --locked streamlit run src/price_viewer/app.py
```

`YOUR_PROJECT_ID`とメールアドレスは実際のプロジェクト値に置き換えます。Google認証のWebブラウザが開きます。ログインは**Token Creator権限を付与された各開発者本人のGoogleアカウント**で行います。使用するシートのIDは各自の環境変数にのみ設定し、Gitに記録しない。

**quota projectのエラー時のみ**、管理者が必要に応じて `roles/serviceusage.serviceUsageConsumer` を対象プロジェクトに付与し、`gcloud auth application-default set-quota-project YOUR_PROJECT_ID` を実行してください。むやみに広いIAMロールを付けないこと。

## 確認方法（情報を貼り付けない）

- `uv run --locked python scripts/run_demo.py` はGoogle認証なしで実行可能。
- `uv run --locked python scripts/analyze_sheet.py` はサービスアカウントの権限で実シートを読み込み、`outputs/analysis/` に結果を出力。
- `403` / token refresh失敗：Sheets API・IAM Service Account Credentials APIの有効化、指定SAに対するToken Creator権限、非公開シートのSA閲覧者共有、quota projectの許可を確認。
- `GOOGLE_APPLICATION_CREDENTIALS` を明示的に設定している場合、そのパスがADCを上書きする。キーJSONの指定をやめる。
- コード/CIへ認証JSON、ローカルADCファイル、シートID、価格実データをコミットしない。
- 権限取り消し後、既発行の短期トークンが有効期限まで残る可能性がある。即時封じ込めが必要ならサービスアカウントのシート共有も外し、影響を確認する。

## 将来の公開・自動化のとき（今は設定しない）

| 実行場所 | 推奨する鍵なし認証 | 注意 |
| --- | --- | --- |
| 開発者のMac/Windows | 人間の認証 + サービスアカウントのなりすましADC | 各人のToken CreatorをSA単位で管理 |
| Google Cloud Run等 | 実行リソースに専用サービスアカウントを関連付ける | 課金・公開前に承認。鍵JSON不要 |
| GitHub Actions等のOIDC環境 | Workload Identity Federation (WIF) + 専用SA | 信頼対象repo/branch/environmentを厳密制限。現時点のCIはモックのみ |
| 他クラウド/オンプレでOIDC等あり | Workload Identity Federation | 対応IdP・運用費・権限設計を別途確認 |

現在のSheets APIコードはADC採用のため、**ローカルなりすまし→将来の実行環境アタッチ/WIF**でアプリ側の認証インターフェースを変更せず移行できます。ただしデプロイやIAM構成・課金は別途人間の承認が必要です。

## 料金と公式資料
- Sheets APIは標準利用に追加料金なし。ただし2026年後半に**標準クォータ超過分の課金が導入予定**。利用規模・Google Cloud全体の料金は導入前に再確認。
- IAM Service Account Credentials APIなど、認証のために有効化するAPIやGoogle Cloudの他サービスも、**無料を無条件で保証しない**。予算アラート/利用量を確認し、課金の有効化は承認後。
- [Google公式：ローカルサービスアカウントのなりすまし](https://cloud.google.com/docs/authentication/use-service-account-impersonation)
- [Google公式：サービスアカウント鍵の回避](https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)
- [Google公式：ADCの検索順序](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Google公式：本番環境のサービスアカウント](https://cloud.google.com/docs/authentication)
- [Google公式：WIF](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Google公式：Sheets APIの料金・クォータ](https://developers.google.com/workspace/sheets/api/limits)
