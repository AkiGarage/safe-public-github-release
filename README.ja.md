# Safe Public GitHub Release Skill

<table>
  <tr>
    <td><a href="README.md">English</a></td>
    <td><strong>日本語</strong></td>
  </tr>
</table>

`safe-public-github-release` は、private / internal な作業リポジトリから
安全に公開用 GitHub release を準備するための Codex skill です。

private な履歴、秘密情報、ローカルパス、メンテナー向けの作業メモを
公開面へ混ぜないことを重視します。

次のような作業で使います。

- private history をそのまま公開せず、clean public snapshot を作る
- `release/vX.Y.Z` branch と PR gate を使って公開前に確認する
- GitHub 上でrenderされた README を見てからmergeする
- Release asset、checksum、visibility flip を公開前後に検証する
- Python tool の TestPyPI / PyPI Trusted Publishing 手順を必要な時だけ確認する

## ローカルインストール

```bash
mkdir -p ~/.codex/skills/safe-public-github-release
rsync -a --delete skill/ ~/.codex/skills/safe-public-github-release/
```

または、このリポジトリのrootで次を実行します。

```bash
scripts/install-local.sh
```

このinstallerは `skill/` の中身をローカルの Codex skills directory にコピー
するだけです。GitHub repository のvisibility変更、tag作成、GitHub Release
公開は行いません。

インストール後は、Codexで次のように呼び出します。

```text
Use $safe-public-github-release to prepare and verify a clean public GitHub release.
```

## Repository Layout

```text
skill/                    Codex skill package
skill/SKILL.md             Main skill instructions
skill/agents/openai.yaml   UI metadata for Codex skill lists
skill/references/          Optional reference material loaded only when needed
scripts/install-local.sh   Sync this repo's skill package into the local Codex skills directory
scripts/validate_skill.py  Local validation checks
```

## このskillが確認すること

公開準備では、速さよりも公開面の安全性を優先します。

- repository、remote、tag、workflow、GitHub visibility を最初に確認する
- public-facing file から秘密情報、private path、handoff note、意図しない生成物を探す
- `release/vX.Y.Z` branch と pull request を使って `main` へmergeする
- READMEやrelease-facing docsを変更した時は、GitHub-rendered READMEを確認する
- tag、release asset、checksum、download済みartifactを公開前後に検証する

## Validate

```bash
python3 scripts/validate_skill.py
```

validatorは、skill packageのmetadata、frontmatter、UI metadata、行末空白、
private local path、secret-like patternを確認します。

## Release Safety Model

新しい公開用repositoryを作る場合は、public-surface gateが通るまでprivateのまま
保ちます。

1. `release/vX.Y.Z` branchで変更を準備する。
2. `main` 宛てにpull requestを開き、validationを走らせる。
3. GitHub-rendered READMEを確認する。
4. tagやrelease作業の前に、repositoryがまだprivateであることを確認する。
5. 明示的なmaintainer approval後にだけvisibilityをpublicへ変更する。

private historyを含むrepositoryをそのまま公開しないでください。公開配布には
clean snapshot repositoryを使います。
