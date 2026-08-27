#!/usr/bin/env python3
"""Small, credential-safe wrapper for zcode-app-cli headless sessions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads((SKILL_DIR / "references" / "defaults.json").read_text(encoding="utf-8"))


def zcode_home(env: dict[str, str] | None = None) -> Path:
    source = env or os.environ
    return Path(source.get("ZCODE_HOME", str(Path.home() / ".zcode"))).expanduser()


def config_path(env: dict[str, str] | None = None) -> Path:
    return zcode_home(env) / "cli" / "config.json"


def load_config(path: Path | None = None) -> dict:
    target = path or config_path()
    if not target.is_file():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def configured(config: dict) -> bool:
    for provider in config.get("provider", {}).values():
        options = provider.get("options", {}) if isinstance(provider, dict) else {}
        if isinstance(options, dict) and bool(options.get("apiKey")):
            return True
    return bool(os.environ.get("ZCODE_API_KEY"))


def catalog(config: dict) -> tuple[list[str], list[str]]:
    models: list[str] = []
    multimodal: list[str] = []
    for provider_id, provider in config.get("provider", {}).items():
        for model_id, meta in (provider.get("models", {}) or {}).items():
            full_id = f"{provider_id}/{model_id}"
            models.append(full_id)
            inputs = (meta.get("modalities", {}) or {}).get("input", []) if isinstance(meta, dict) else []
            if isinstance(meta, dict) and (meta.get("attachment") or meta.get("supportsImages") or "image" in inputs):
                multimodal.append(full_id)
    return sorted(models), sorted(multimodal)


def command_version(executable: str) -> str | None:
    try:
        result = subprocess.run([executable, "--version"], text=True, capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or result.stderr.strip() or None


def status() -> dict:
    executable = shutil.which("zcode")
    cfg_path = config_path()
    cfg = load_config(cfg_path)
    models, multimodal = catalog(cfg)
    model_block = cfg.get("model", {}) if isinstance(cfg.get("model", {}), dict) else {}
    return {
        "installed": bool(executable),
        "executable": executable,
        "version": command_version(executable) if executable else None,
        "zcode_home": str(zcode_home()),
        "config_path": str(cfg_path),
        "config_valid": bool(cfg),
        "main_model": model_block.get("main"),
        "lite_model": model_block.get("lite"),
        "models": models,
        "multimodal_models": multimodal,
        "required_models_present": all(item in models for item in DEFAULTS["compatible_models"]),
        "model_access_configured": configured(cfg),
        "setup_pending": (cfg_path.parent / "setup-pending").exists(),
        "session_db_exists": (zcode_home() / "cli" / "db" / "db.sqlite").is_file(),
    }


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    raise ValueError("provide --prompt or --prompt-file")


def terminate_owned_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
    else:
        process.kill()


def invoke_raw(directory: Path, prompt: str, mode: str, timeout: int,
               session_id: str | None = None, env: dict[str, str] | None = None) -> dict:
    executable = shutil.which("zcode")
    if not executable:
        return {"ok": False, "error": "zcode_not_found"}
    command = [executable, "--prompt", prompt, "--cwd", str(directory), "--mode", mode, "--json", "--no-color"]
    if session_id:
        if not session_id.startswith("sess_"):
            return {"ok": False, "error": "invalid_session_id"}
        command.extend(["--resume", session_id])
    process = subprocess.Popen(command, cwd=directory, env=env, text=True, encoding="utf-8",
                               errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_owned_process(process)
        stdout, stderr = process.communicate()
        return {"ok": False, "error": "timeout", "pid": process.pid,
                "stdout": stdout.strip(), "stderr": stderr.strip()}
    parsed = None
    try:
        parsed = json.loads(stdout) if stdout.strip() else None
    except json.JSONDecodeError:
        pass
    return {"ok": process.returncode == 0, "exit_code": process.returncode, "pid": process.pid,
            "session_id": session_id or (parsed.get("session_id") if isinstance(parsed, dict) else None),
            "result": parsed, "stdout": stdout.strip() if parsed is None else None,
            "stderr": stderr.strip() or None}


def smoke_test(directory: Path, timeout: int) -> dict:
    cfg = load_config()
    if not configured(cfg):
        return {"ok": False, "error": "model_access_not_configured"}
    with tempfile.TemporaryDirectory(prefix="codex-zcode-smoke-") as temp:
        temp_home = Path(temp) / ".zcode"
        target = temp_home / "cli" / "config.json"
        target.parent.mkdir(parents=True)
        shutil.copy2(config_path(), target)
        env = os.environ.copy()
        env["ZCODE_HOME"] = str(temp_home)
        result = invoke_raw(directory, f'Reply exactly {DEFAULTS["smoke_reply"]}', "plan", timeout, env=env)
        output = json.dumps(result.get("result"), ensure_ascii=False) if result.get("result") else (result.get("stdout") or "")
        result["expected_reply_found"] = DEFAULTS["smoke_reply"] in output
        result["isolated_home"] = True
        result["ok"] = bool(result.get("ok") and result["expected_reply_found"])
        return result


def emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_status = sub.add_parser("status")
    p_status.add_argument("--json", action="store_true")
    for name in ("invoke", "smoke-test"):
        p = sub.add_parser(name)
        p.add_argument("--dir", required=True)
        p.add_argument("--timeout", type=int, default=DEFAULTS["smoke_timeout_seconds"] if name == "smoke-test" else DEFAULTS["invoke_timeout_seconds"])
        p.add_argument("--json", action="store_true")
        if name == "invoke":
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument("--prompt")
            group.add_argument("--prompt-file")
            p.add_argument("--mode", choices=("build", "edit", "plan", "yolo"), default="build")
            p.add_argument("--session-id")
    args = parser.parse_args()
    if args.command == "status":
        payload = status()
    else:
        directory = Path(args.dir).resolve()
        if not directory.is_dir():
            payload = {"ok": False, "error": "directory_not_found", "directory": str(directory)}
        elif args.command == "smoke-test":
            payload = smoke_test(directory, args.timeout)
        else:
            payload = invoke_raw(directory, read_prompt(args), args.mode, args.timeout, args.session_id)
    emit(payload, args.json)
    return 0 if payload.get("ok", payload.get("installed", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
