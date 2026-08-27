# Codex ZCode Session

A Codex Skill for running and inspecting local ZCode CLI sessions on Windows. It supports credential-safe status checks, headless prompts, exact session resume, model catalog inspection, and an isolated smoke test.

## Models

The supplied defaults use `zai/glm-5.3` for primary work and `zai/glm-5.3-flash` for lightweight or multimodal work. `zai/glm-5.2` remains available for compatibility. GLM-5.3-Flash is declared for text, image, PDF, and video input.

## Install

Copy this repository to `~/.codex/skills/codex-zcode-session`, then check the local client:

```powershell
python .\scripts\zcode_session.py status --json
```

The compatible terminal client is [`zcode-app-cli`](https://github.com/kingsword09/zcode-cli), an unofficial client that embeds the official agent runtime distributed with ZCode Desktop. It requires Node.js 22.19 or newer.

## Use

```powershell
python .\scripts\zcode_session.py invoke `
  --dir C:\path\to\repo --prompt "Inspect the failing tests" --mode plan --json

python .\scripts\zcode_session.py invoke `
  --dir C:\path\to\repo --session-id sess_example `
  --prompt-file .\next-step.txt --json
```

On Windows, configure a Z.AI or BigModel Coding Plan key through the masked TUI setup. Never commit a populated ZCode user configuration.

## Validation

```powershell
python C:\path\to\skill-creator\scripts\quick_validate.py .
python .\scripts\zcode_session.py status --json
```

MIT licensed. This project is independent of Z.ai and the `zcode-app-cli` project.
