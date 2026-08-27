---
name: codex-zcode-session
description: 在用户要求安装后检查、配置、启动、继续、监督或排查本机 ZCode CLI 会话，或希望使用 GLM-5.2、GLM-5.3、GLM-5.3-Flash 完成编码任务时使用；覆盖 Windows 无头调用、模型检查、准确会话恢复和隔离测试。不用于操作 ZCode Desktop 图形界面。
---

# Codex ZCode Session

将 ZCode CLI 作为本机外部编码协作者。Codex 先确认任务、工作目录与现有改动，ZCode 在用户许可的目录中工作，Codex随后检查真实文件和测试结果。

## 开始前

1. 运行状态检查：

   ```powershell
   python <skill-dir>\scripts\zcode_session.py status --json
   ```

2. 确认准确工作目录，阅读适用的项目说明、`git status --short`、现有差异和测试命令。
3. 安装、升级、登录、修改长期配置、提交、推送、公开分享、发布或部署需要用户明确提出。
4. `zcode-app-cli` 是对 ZCode Desktop 所带官方 agent runtime 的非官方终端客户端。需要说明来源时保持这一表述。

## 模型与登录

状态结果应包含当前主模型、轻量任务模型、可见模型和多模态能力。当前推荐配置为：

- 主模型：`zai/glm-5.3`
- 轻量任务：`zai/glm-5.3-flash`
- 可选兼容模型：`zai/glm-5.2`

`glm-5.3-flash` 支持图片、PDF 和视频输入。模型出现在配置中只表示可以选择；只有真实请求返回正确内容，才能说明访问有效。

Windows 上的 Z.AI OAuth 回调不适用于此社区客户端。若状态显示 `model_access_configured: false`，请让用户在 ZCode TUI 的遮蔽输入界面选择 Coding Plan API Key；不得在命令行、日志、提示文件或仓库中写入密钥。

## 调用与继续

长提示先写入 UTF-8 文件：

```powershell
python <skill-dir>\scripts\zcode_session.py invoke `
  --dir <repo> --prompt-file <prompt.txt> --mode build --json
```

只读检查使用 `--mode plan`。继续会话时必须提供准确 ID，并保持原工作目录：

```powershell
python <skill-dir>\scripts\zcode_session.py invoke `
  --dir <repo> --session-id <sess_id> --prompt-file <prompt.txt> --json
```

不要用 `--continue` 自动选择最近会话。收到结果后检查实际差异、进程和测试；ZCode 的文字说明或退出状态不能单独证明任务完成。

## 真实测试

首次配置凭据、客户端更新或脚本修改后运行：

```powershell
python <skill-dir>\scripts\zcode_session.py smoke-test `
  --dir <safe-dir> --json
```

测试在临时 `ZCODE_HOME` 中运行，只复制必要配置，使用 `plan` 模式并在结束后删除临时数据。若凭据尚未配置，测试应明确报告 `model_access_not_configured`，不得伪造成功。

## 操作要求

- 只在用户许可的目录和任务范围内使用无头模式。
- 保留已有文件和无关改动，不自行执行 commit、push、reset、clean、stash 或批量删除。
- 不按进程名终止 ZCode；超时时只停止辅助脚本启动的准确进程树。
- 日志和回复不得显示凭据、认证头或完整私有配置。
- 详细的会话、超时与结果字段见 [references/operation-protocol.md](references/operation-protocol.md)。
