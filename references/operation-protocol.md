# Operation protocol

## Status

`status` is read-only. It reports executable discovery, versions, selected models, catalog entries, multimodal entries, configuration location, database presence, and whether model access appears configured. It never returns an API key.

## Invocation

`invoke` uses `zcode --prompt`, an explicit working directory, an explicit permission mode, JSON output, and an optional exact `sess_...` ID. Prompt files are decoded as UTF-8.

The command's process group belongs to the helper invocation. On Windows, timeout cleanup uses `taskkill /PID <pid> /T /F` for that exact PID only.

## Smoke test

The smoke test requires configured model access. It copies the credential-bearing config into a temporary `ZCODE_HOME`, never prints it, uses `plan` mode, checks the fixed reply, and deletes the temporary directory when the subprocess exits.

## Result interpretation

A zero exit code does not verify repository changes. Inspect `git diff`, affected files, expected tests, and any remaining child processes. When resuming, verify both the session ID and its original working directory.
