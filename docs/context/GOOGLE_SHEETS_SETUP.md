# 非公開Googleスプレッドシートの設定（操作担当者向け）

## 先に確認：無料枠とリスク（2026-11-14時点）

- Google Sheets APIの**標準利用は追加料金なし**。読み取りはGoogle公式掲載の標準値で「毎分300件/プロジェクト」「毎分60件/ユーザー/プロジェクト」。実際の割り当てはプロジェクトのGoogle Cloud Consoleで確認する。
- Googleは**2026年後半に標準枠を超えるAPI利用に課金を導入する予定**と説明しているため、将来も無料とは保証できない。料金プランの新情報・上限変更は定期確認する。
- 本実装は2シートを**1回のbatchGet**で読み取り、画面は5分キャッシュ、429時のみ最大2回再試行。API回数をむやみに増やさない。料金回避のため、現段階では**Google Cloud課金を有効にしない**方針。キーレス認証のためIAM Credentials APIの有効化が必要。利用可能なサービス・クォータは実際のプロジェクトで要確認。
- 無料枠は「無制限」という意味ではない。API以外（Cloud Run、Cloud Storage、LLM API等）は別料金になり得る。

公式資料：
- [Google Sheets API使用制限・料金](https://developers.google.com/workspace/sheets/api/limits)
- [Google Workspaceの2026年標準利用モデル](https://developers.google.com/workspace/tools-safety)
- [Google Cloudでクォータを確認](https://console.cloud.google.com/iam-admin/quotas)

## 1. 入力用スプレッドシートを作る

1. 個人または共同管理用Googleアカウントで [Google Sheets](https://sheets.google.com/) を開いて新しいスプレッドシートを作る。既存Excelをインポートする場合は、権限・データ型を再点検する。
2. シート（タブ）名を**`価格履歴`** と **`商品マスタ`** にする（シート名を変更するとAPIでエラー）。
3. A1〜D1に `確認日`、`商品ID`、`価格`、`備考`。商品マスタのA1〜B1に `商品ID`、`商品名` と入力。その他の列はこの試作では読み込まない。
4. **商品ID列を「表示形式 → 数字 → 書式なしテキスト」に変更してから入力**（`001`と`1`を混同しない）。価格は円の数値セル（例 `95000`）、確認日は日付セル。日付は表示形式 `yyyy-mm-dd` または `yyyy/mm/dd` 推奨。
5. 右上の「共有」を開く →「一般的なアクセス」を**制限付き**にする。実際に編集する人のGoogleアカウントを**編集者**、分析だけする人は**閲覧者**に設定。全員にURLを知るだけでアクセスできるようにはしない。

## 2. Google CloudプロジェクトとAPIを用意する（管理者1人）

1. [Google Cloud Console](https://console.cloud.google.com/) を開く。Googleアカウントでログイン。
2. 画面上部のプロジェクト選択から**新しいプロジェクト**を作成。例：`joint-price-analysis`。
3. 「APIとサービス → ライブラリ」で **Google Sheets API** を探し、「有効にする」。この実装ではGoogle Drive APIは使用しない。
4. 「IAMと管理 → サービス アカウント → サービスアカウントを作成」。例：`sheet-price-reader`。Google Cloudの強いIAMロールは不要（スプレッドシート本体への共有で許可する）。
5. 作成したサービスアカウントのメールアドレス（例 `sheet-price-reader@PROJECT_ID.iam.gserviceaccount.com`）を控える。
6. スプレッドシートに戻り「共有」でサービスアカウントのメールを追加し、**閲覧者**を選ぶ。サービスアカウントはメールを受け取らないので通知は不要。これでSheets APIがこの1ファイルを読める。

公式：[Google Workspace認証情報の作成・ファイル単位共有](https://developers.google.com/workspace/guides/create-credentials)

## 3. 開発者のキーレス認証（長期秘密鍵JSONは作らない）

**チーム標準は Google Cloud CLIによる「サービスアカウントのなりすまし＋ADC」です。** 公式案内ではキーJSONより安全で、2人から人数が増えても各人のIAM権限を個別に剥奪できます。

まず[キーレス認証の詳細と公式出典](KEYLESS_AUTH.md)を参照してください。

1. 管理者はGoogle Cloudで **IAM Service Account Credentials API** を有効化（Sheets APIに加えて必要）。
2. 対象のサービスアカウント自体の「権限」で、開発者個人のGoogleアカウントに **サービス アカウント トークン作成者**（`roles/iam.serviceAccountTokenCreator`）を付与。**プロジェクト全体への付与は避ける。**
3. 秘密鍵JSONの作成は行わない。サービスアカウントは非公開シートで**閲覧者**に設定し、入力担当者は別途**編集者**に設定。
4. 各人のPCに[Google Cloud CLI](https://cloud.google.com/sdk/docs/install)をインストールし、各自で `gcloud auth login` および `gcloud auth application-default login --impersonate-service-account=SERVICE_ACCOUNT_EMAIL` を実行。
5. `GOOGLE_APPLICATION_CREDENTIALS` に古いサービスアカウント鍵JSONを設定していた場合は**解除**する（この環境変数はローカルADCより優先される）。シートIDだけ `GOOGLE_SHEET_ID` で設定。

[Windows/macOS別の操作コマンド](OS_SETUP.md)を使用。PC上のADCには開発者本人の認証情報が保存されるので、個人別OSアカウントで安全に保護すること。ログイン情報や認証ファイルをGitHubに入れない。

## 4. 動作確認と権限

- Google認証なしでも `uv run --locked python scripts/run_demo.py` は動作する。
- 設定後に `uv run --locked python scripts/analyze_sheet.py` を実行し、`outputs/analysis/` にHTML/CSVが作成されたらAPIの読取成功。
- `403`：非公開シートのSA閲覧権限、SA単位のToken Creator権限、Sheets / IAM Credentials APIの有効化を確認。
- `404`：スプレッドシートIDやアクセス権を確認。
- `400`：シート名 `価格履歴`・`商品マスタ` と列ヘッダーを確認。
- `429`：利用上限。コードは少数の再試行後停止する（無限リクエストしない）。
- 問題が出てもADC認証情報・トークン・AuthorizationヘッダーをPRに貼らない。

## 5. 課金を防ぐチェック

- [Google Cloud Console](https://console.cloud.google.com/) →「APIとサービス」→「Google Sheets API」→クォータと使用状況を定期確認。
- 意図しないGoogle Cloudサービスを有効化しない。現段階ではCloud Billingアカウントを接続しない運用を推奨。
- 定期取得・公開Webアプリなどで呼び出し数が増える前にGoogle公式の**最新料金と上限**を再確認し、費用の承認ゲートを設ける。
