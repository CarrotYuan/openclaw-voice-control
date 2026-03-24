---
name: openclaw-voice-control
description: Local macOS voice-control integration for OpenClaw. Use when setting up, deploying, troubleshooting, or operating wakeword-triggered voice access to a local OpenClaw agent with ASR, TTS, overlay UI, and launchd background support.
---

# OpenClaw Voice Control

`OpenClaw Voice Control` 是一个运行在 macOS 上的本地语音控制集成层，用来给 OpenClaw 提供语音唤起、语音识别、语音播报、浮窗和后台常驻能力。

项目仓库来源：

- GitHub：[CarrotYuan/openclaw-voice-control](https://github.com/CarrotYuan/openclaw-voice-control)

它提供：

- 唤醒词触发
- 本地麦克风录音
- 基于 FunASR / SenseVoice 的本地语音识别
- 将识别后的文本发送给本地 OpenClaw 智能体
- 使用 macOS TTS 播报回复
- 可选浮窗 UI
- 基于 `launchd` 的后台常驻
- 用户登录后的自动启动

## 平台范围

- 仅支持 macOS

## 安全边界提醒

这个 Skill 提供的是一个语音入口，而这个入口并不绑定某一个人的身份。

这意味着：

- 麦克风附近的任何人都可能触发它
- 连接到这个语音入口的 OpenClaw 智能体，其能力也可能被语音触发到

因此强烈建议：

- 给目标智能体提示词加入明确的安全约束
- 对高风险操作增加确认步骤
- 不要给语音入口对应的智能体过宽的自动化权限
- 对外部工具和系统使用最小权限原则

## 主线安装路径

把这个 Skill 理解成一个“本地部署型 Skill”，而不是普通提示词。

当它被安装到 OpenClaw 后：

- 默认从当前对话智能体所加载的 skill 目录开始操作
- 以这里声明的 GitHub 仓库为唯一可信来源
- 不要擅自切换到别的本地克隆目录或已经配好的旧环境
- 在目录里只有 `SKILL.md` 的情况下，不要继续部署

主安装文档是克隆后仓库里的 `README.md`。  
`README.zh-CN.md` 是中文辅助说明。

标准安装主线：

1. 把完整项目仓库同步到当前已安装的 skill 工作目录
2. 创建并激活 `.venv`
3. 执行 `pip install -e .`
4. 下载或补齐 SenseVoice 模型目录
5. 下载或补齐 VAD 模型目录
6. 从 `.env.example` 复制出 `.env`
7. 在 `.env` 中填好必填配置项
8. 使用默认的 openWakeWord 路线
9. 先做前台验证
10. 询问用户是否需要后台常驻与自启动
11. 如果需要，再执行 `./scripts/deploy_macos.sh`
12. 如果不需要，则停在前台运行方案

最短命令路径：

```bash
# 从当前对话智能体所加载的 skill 目录开始
git init
git remote add origin https://github.com/CarrotYuan/openclaw-voice-control.git
git fetch --depth 1 origin main
git checkout -B main FETCH_HEAD
# 确认当前目录里已经有 scripts/、src/、config/、launchagents/、README.md
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
cp .env.example .env
python -m openclaw_voice_control --config config/default.yaml --env-file .env
```

## 开始前需要具备什么

在真正跑起来之前，请先确保这些前置条件存在或可被提供：

- Python 3.11 或更高版本
- 一个正在运行的本地 OpenClaw 服务
- `OPENCLAW_TOKEN`
- macOS 麦克风权限
- 一种可以下载 SenseVoice 和 VAD 模型目录的方式

对默认路线来说，剩下这些步骤一般都可以由 AI 或操作者按文档自动完成：

- 从 `.env.example` 复制 `.env`
- 下载 SenseVoice 模型目录
- 下载或补齐 VAD 模型目录
- 在首次运行时让 openWakeWord 自动下载所选的预训练唤醒词模型

## 推荐默认路线

默认推荐：

- `WAKEWORD_PROVIDER=openwakeword`
- `OPENWAKEWORD_MODEL_NAME=hey jarvis`
- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

除非用户明确要求，否则优先采用这条默认路线。

## 可选 Porcupine 路线

Picovoice / Porcupine 现在是可选备选方案，不是默认路线。

只有在用户明确要求继续使用本地 `.ppn` 唤醒词模型时，才切换到这条路线。

如果选择它，需要配置：

- `WAKEWORD_PROVIDER=porcupine`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`

## 切换 openWakeWord 唤醒词

如果要切换默认的 openWakeWord 唤醒词，修改：

- `OPENWAKEWORD_MODEL_NAME`

当前更适合作为通用唤醒词的官方预训练名称包括：

- `hey jarvis`
- `hey mycroft`
- `hey rhasspy`
- `alexa`

这些预训练模型会在首次使用时自动下载。

当前代码已经支持通过修改 `OPENWAKEWORD_MODEL_NAME` 切换这些官方预训练名称，但目前在这个仓库里真正做过 smoke test 的仍然只有默认的 `hey jarvis` 路线。

## 执行规则

使用这个 Skill 时，请遵守这些规则：

1. 优先使用这里声明的 GitHub 仓库。
   - 从 `https://github.com/CarrotYuan/openclaw-voice-control.git` 开始。
   - 不要因为看到别的相似仓库就自行替换。

2. 部署工作保持在当前已安装的 skill 工作目录内。
   - 不要擅自切换到别的本地克隆目录。
   - 如果 GitHub 拉取失败且本地已有克隆，必须先问用户。

3. 不要擅自复用旧环境。
   - 不要默认复用现成 `.venv`、本地模型缓存、旧 `.env` 或私有运行环境。
   - 如果复用缓存可能节省时间，也要先说明并征求同意。

4. 不要编造缺失值。
   - 写 `.env` 时必须使用项目要求的真实变量名，尤其是 `OPENCLAW_TOKEN`。
   - 如果关键配置或本地资源缺失，就停下来并指向文档中的真实来源。

5. 谨慎处理敏感信息。
   - 不要把真实 token 或 key 明文回显到对话里，除非用户明确要求查看。
   - 对这个项目，OpenClaw token 只从 `~/.openclaw/openclaw.json` 的 `gateway` 配置获取。
   - 不要使用 `~/.openclaw/identity/device-auth.json` 作为这个项目的 token 来源。

6. 前台验证优先，后台部署要先征求用户确认。
   - 当前台验证成功后，再问用户是否需要后台常驻与自启动。
   - 只有用户明确需要时，才执行 `./scripts/deploy_macos.sh`。

## 日常维护

主要脚本：

- 部署后台常驻：`./scripts/deploy_macos.sh`
- 重启已安装的后台服务：`./scripts/restart_service.sh`
- 卸载已安装的后台服务：`./scripts/uninstall_macos.sh`
- 检查本地安装和环境问题：`./scripts/doctor.sh`

如果用户更习惯 Finder，也可以使用 `scripts/` 目录里的 `.command` 包装脚本。

## 两种关闭意图

把“关闭语音”类请求只区分成两种用户意图：

- 临时关闭语音功能
  - 停止当前前台进程，或停止已部署的后台运行时
  - 不删除 skill 文件夹
- 直接删除 skill
  - 删除 skill 文件夹本身
  - 只有在用户明确要求彻底删除时才这样做

如果用户说的是“关掉它”“停止语音”这类模糊表达，先追问一句，不要自己猜。

## 背景架构

当前保留并推荐的后台方案是：

- `launchd -> host app -> shell script -> python`

`./scripts/deploy_macos.sh` 会自动构建所需的 host app。

## 主要配置项

主要配置项有：

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `OPENCLAW_AGENT_ID`
- `OPENCLAW_MODEL`
- `OPENCLAW_USER`
- `WAKEWORD_PROVIDER`
- `OPENWAKEWORD_MODEL_NAME`
- `OPENWAKEWORD_MODEL_PATH`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

如果用户明确切换到可选 Porcupine 路线，再额外配置：

- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`

以下两个变量仍然保留：

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

它们只是排障用，不是当前推荐的主方案。

`OPENWAKEWORD_THRESHOLD` 这个变量仍然保留，但它更适合放在排障和调参场景里，而不是首次安装的主线配置项。

一般来说，机器相关的密钥和路径写进 `.env`，而 wakeword 的阈值、重新武装时间这类调参项应优先改 `config/default.yaml`。

## 缺失项从哪里获取

把项目仓库同步到当前工作目录后，查看 `README.md` 里的这三节：

- `What Must Exist Before Setup`
- `Required Variables`
- `Where To Get Each Requirement`

最常用的来源说明：

- `OPENCLAW_TOKEN`：从 `~/.openclaw/openclaw.json` 的 `gateway` 配置获取
- 默认唤醒词路线：使用 openWakeWord 自带的英文 `hey jarvis`
- 可选 Porcupine 路线：`PICOVOICE_ACCESS_KEY` 和本地 `.ppn` 从 [Picovoice](https://picovoice.ai/) 获取
- 如果 GitHub 拉取失败，先报告失败，不要直接切换到不相关的本地目录

## 相关文件

- 克隆后的仓库中的 `README.md`
- 克隆后的仓库中的 `README.zh-CN.md`
- 克隆后的仓库中的 `docs/macos-install.md`
