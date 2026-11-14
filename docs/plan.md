# 価格分析の開発計画（更新：2026-11-14）

かつて採用したExcel原本をGitHubで追跡する設計は、チームでの手間・二重管理・バイナリ差分の問題があるため、**ADR 0004で非公開Googleスプレッドシートへ置き換える提案**となった。

## 現在の分析MVP

- [Google Sheets API接続・認証](context/GOOGLE_SHEETS_SETUP.md)
- [データ契約・見出し](context/DATA_CONTRACT.md)
- [Google Sheets版アーキテクチャ](context/ARCHITECTURE.md)
- [受け入れテスト仕様](context/ANALYSIS_MVP_SPEC.md)
- [WindowsとmacOSの操作手順](context/OS_SETUP.md)
- [AIのPDCAと人間の承認ゲート](context/LOOP_ENGINEERING.md)

## 次の開発フェーズ

1. 本移行PRの承認・マージ、Google側のアクセス設定。
2. 実Googleシートに入力したデータとの結合テスト、商品ID/日付の表記ゆれ確認。
3. 店舗ID・商品状態・価格の出所を保持するデータ設計の承認。
4. 価格差、為替調整、外部指標との統計検証を経た上で異常検知やAI分析を検討。

実測データを使った経済予測精度は未検証。テスト用の価格は架空。
