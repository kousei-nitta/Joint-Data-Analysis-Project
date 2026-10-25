# 開発の進め方

## 1. 実装前に方針を決める

目的・入力・画面・完成条件を先に確認し、合意してからアプリのコードを書きます。
AIにも作業範囲と完了条件を伝え、無関係な変更や実データの書き換えを避けます。

## 2. タスクごとにブランチを作る

作業中の変更がないことを確認してから実行します。

```bash
git switch main
git pull --ff-only
git switch -c feat/price-chart
uv sync --locked
```

`feat/price-chart` は例です。機能には `feat/`、修正には `fix/`、基盤整備には `chore/` を使います。

## 3. 確認してcommit・push・PR

```bash
uv lock --check
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked python scripts/check_environment.py
git diff --check
git status
```

アプリ実装後は意味のあるテストを `tests/` に追加し、`uv run --locked pytest` をCIにも追加します。
現段階ではテストが未作成のため、pytestの実行は必須にしていません。

```bash
git add <今回変更したファイル>
git commit -m "feat: 価格推移の表示を追加"
git push -u origin HEAD
gh pr create --base main
```

GitHub CLIを使う場合は `brew install gh` と `gh auth login` が初回のみ必要です。
ブラウザのGitHubからPRを作成しても構いません。
PRに変更目的・確認結果・未実装部分を記載し、ユーザーのレビューとマージを待ちます。
mainへ直接pushしたり、レビュー前にマージしたりしません。

## ライブラリを変更するとき

`uv add <ライブラリ名>`（開発用は `uv add --dev <名前>`）を使い、
`pyproject.toml` と `uv.lock` を同じPRで更新します。
Pythonやuvの更新は別タスクとして確認し、設定・手順・CIを揃えます。
`.venv`、個人データ、生成物、認証情報はcommitしません。
既に追跡されている `product_prices.xlsx` の変更はGitで共有されるため、差分を意識してください。
