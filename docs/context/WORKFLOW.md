# 人間＋複数AIによる開発ワークフロー

## 情報をどこに残すか
| 情報 | 正本の置き場所 |
| --- | --- |
| 目的・非目標 | `PROJECT_BRIEF.md` |
| 現状・設計・データ契約 | `ARCHITECTURE.md` / `DATA_CONTRACT.md` / `CURRENT_STATUS.md` |
| 重要な選択肢・採否 | `docs/adr/` |
| タスクの目的・完了条件 | GitHub Issue またはPR本文 |
| 実装 | コード・テスト |
| セッション引き継ぎ | `HANDOFF_TEMPLATE.md`（タスクごとに複製） |

チャットの履歴、生成AIの内部記憶、プロンプト内だけに決定事項を残さない。どのモデルで作業しても同じ参照先に辿り着けることを優先する。

## 1タスクの流れ
1. 作業開始：`main` と最新ドキュメントを確認。Issue/依頼で目的と完了条件を決める。
2. ブランチ：`feat/`、`fix/`、`chore/` のいずれか。直接mainへコミットしない。
3. 実装：既存Excel原本の保全、テストデータの明示、機能とドキュメントの同期。
4. 検証：`uv sync --locked`、`uv run --locked ruff check .`、`uv run --locked ruff format --check .`、`uv run --locked python scripts/check_environment.py`。テスト追加時は `uv run --locked pytest`。
5. PR：目的/変更点/実行したチェック/未検証点/次のタスク/設計上の判断を記載。
6. 人間がレビューして承認したときのみmainにマージ。AIは勝手にマージしない。

## AIに依頼する際の最小プロンプト
> リポジトリの `AGENTS.md` と `docs/context/CURRENT_STATUS.md`、関連仕様を先に読み、現在のコードを事実として確認してください。今回の目的は【...】、変更対象は【...】、受け入れ条件は【...】です。変更は専用ブランチ/PRに限定し、データ原本とmainを変更しないでください。検証結果と未確認事項をPRに残してください。

外部のAIにファイルアクセス権がない場合は、上記ファイルと対象コードを明示的に提供する。機密をAIへ貼り付けない。

## 役割（2人・各週5〜10時間の想定）
- データ/仮説担当：店舗候補と出所検証、Excel入力内容の確認、分析定義、出力レビュー。
- 実装担当：Python処理、テスト、Git/CI、再現可能性の維持。
- 両名：仕様・ADR・PRをレビュー。経験差があっても成果物単位で分業する。

## コンテキストの更新ルール
コード仕様が変われば `DATA_CONTRACT.md`・`ARCHITECTURE.md`・`CURRENT_STATUS.md` を更新。重要判断はADRで採否と理由を残す。週次または節目に `CURRENT_STATUS.md` を更新して「現在地」を共有する。

## 自律的な検証と人間の承認

セッション内でAIが反復的にテスト・改善する詳細は[LOOP_ENGINEERING.md](LOOP_ENGINEERING.md)を参照。自動テスト合格はmainマージの承認を代替しない。入力担当者のExcel更新も承認後に別PRで検証する。OS別手順は[OS_SETUP.md](OS_SETUP.md)。
