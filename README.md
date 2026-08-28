<p align="center">
  <picture>
    <source media="(max-width: 680px)" srcset="./assets/readme/hero-mobile.svg">
    <img src="./assets/readme/hero.svg" width="100%" alt="Any-to-ZCode: route work from any compatible harness to exact ZCode sessions">
  </picture>
</p>

<p align="center">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/ZiChenWang114514/Any-to-ZCode/actions/workflows/ci.yml"><img src="https://github.com/ZiChenWang114514/Any-to-ZCode/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  · Windows · Python 3.10+ · MIT
</p>

# Any-to-ZCode

Connect any compatible coding harness to local ZCode CLI sessions. The adapter reports the active GLM route without printing credentials, runs a headless task in an explicit directory, and resumes one exact `sess_...` conversation.

This repository is a local session adapter: a Python CLI, plus a Codex Skill wrapper. It is independent of Z.ai and of the `zcode-app-cli` maintainers.

## What is verified

| Check | Current evidence |
| --- | --- |
| Skill structure and Python wrapper | Validated in CI on Windows |
| ZCode runtime discovery | `zcode-app-cli 3.9.2-16`, runtime `0.16.5` |
| Model catalog | GLM-5.2, GLM-5.3 and GLM-5.3-Flash detected |
| Multimodal declaration | GLM-5.3-Flash declares image, PDF and video input |
| Live GLM response | Requires a configured Coding Plan key; catalog visibility alone does not prove access |

## What it does

- Resume by full session ID and keep the original working directory. The helper does not use ZCode's "latest session" shortcut.
- Return versions, selected models, multimodal entries, and setup state as JSON.
- Choose `plan`, `build`, `edit`, or `yolo` for each headless request.
- Run the smoke test in a temporary `ZCODE_HOME` and remove that test data afterward.
- Accept long instructions from UTF-8 prompt files instead of shell quoting.

Codex, Claude Code, Grok Build, and other tools can call the Python CLI. Codex users can also invoke `$codex-zcode-session` after installing the Skill.

## Install

This adapter targets [`zcode-app-cli`](https://github.com/kingsword09/zcode-cli), an unofficial terminal client for the official agent runtime shipped with ZCode Desktop.

```powershell
npm install -g zcode-app-cli@latest
zcode --version
```

Node.js 22.19 or newer is required. On Windows, open `zcode` once and configure a Z.AI or BigModel Coding Plan key through the masked setup interface.

```powershell
git clone https://github.com/ZiChenWang114514/Any-to-ZCode.git `
  "$env:USERPROFILE\.codex\skills\codex-zcode-session"
```

The clone destination is the Codex Skill id, `codex-zcode-session`. Other harnesses can run `scripts/zcode_session.py` directly.

## First use

```powershell
python "$env:USERPROFILE\.codex\skills\codex-zcode-session\scripts\zcode_session.py" `
  status --json
```

A useful first result looks like:

```json
{
  "main_model": "zai/glm-5.3",
  "lite_model": "zai/glm-5.3-flash",
  "required_models_present": true,
  "model_access_configured": false
}
```

`model_access_configured: false` means the catalog is installed, but a live model request should not be reported as successful yet.

Use `plan` for read-only analysis:

```powershell
python .\scripts\zcode_session.py invoke `
  --dir C:\path\to\repo `
  --prompt "Inspect the failing tests and explain the cause." `
  --mode plan --json
```

Use a UTF-8 prompt file for implementation work:

```powershell
python .\scripts\zcode_session.py invoke `
  --dir C:\path\to\repo `
  --prompt-file .\phase-1.txt `
  --mode build --json
```

Continue the same conversation with its complete ID:

```powershell
python .\scripts\zcode_session.py invoke `
  --dir C:\path\to\repo `
  --session-id sess_xxxxxxxx `
  --prompt-file .\phase-2.txt --json
```

## Model routing

| Role | Model | Input |
| --- | --- | --- |
| Primary work | `zai/glm-5.3` | Text |
| Lightweight and multimodal work | `zai/glm-5.3-flash` | Text, image, PDF, video |
| Compatibility option | `zai/glm-5.2` | Text |

Changing the user configuration affects newly created sessions. A resumed session may keep the model stored in its history.

## Verification

1. Run `status --json` and confirm the executable, model IDs, and credential state.
2. Review the target repository instructions, current changes, and test commands.
3. Start `invoke` with an explicit directory, prompt, and permission mode.
4. Inspect the actual file changes and run the repository's own tests.
5. Continue only with the exact session ID returned by the first call.

After model access is configured:

```powershell
python .\scripts\zcode_session.py smoke-test `
  --dir C:\path\to\safe-dir --json
```

## Using it from a coding agent

```text
Use $codex-zcode-session in C:\path\to\repo.
Check status, then start a plan-mode session that explains the failing tests.
Do not edit files.
```

## Safety notes

- Credentials are checked only as present or absent; their values are never printed.
- Timeout cleanup targets only the process started by the wrapper.
- The adapter does not commit, push, publish, or alter unrelated files.
- A successful CLI exit still requires inspection of repository changes and tests.

## Machine-readable contract

Every command accepts `--json`. The shared fields are `schema_version`, `ok`, `target`, `command`, `provider`, `workdir`, `session_id`, `requested_model`, `actual_model`, `result`, `warnings`, and `error`. Adapter-specific evidence remains alongside them.

## Related adapters

| Repository | Target |
| --- | --- |
| [Any-to-OpenCode](https://github.com/ZiChenWang114514/Any-to-OpenCode) | OpenCode |
| [Any-to-Grok-Build](https://github.com/ZiChenWang114514/Any-to-Grok-Build) | Grok Build |
| [Any-to-Kimi-Code](https://github.com/ZiChenWang114514/Any-to-Kimi-Code) | Kimi Code |
| [Any-to-DeepSeek-Harness](https://github.com/ZiChenWang114514/Any-to-DeepSeek-Harness) | DeepSeek Harness |
| [Any-to-Codex](https://github.com/ZiChenWang114514/Any-to-Codex) | Codex CLI |
| [Any-to-Claude-Code](https://github.com/ZiChenWang114514/Any-to-Claude-Code) | Claude Code |
| [Any-to-Pi](https://github.com/ZiChenWang114514/Any-to-Pi) | Pi |

## License

[MIT](./LICENSE). ZCode CLI behavior can change with the embedded runtime, so re-run `status` and the smoke test after upgrades.
