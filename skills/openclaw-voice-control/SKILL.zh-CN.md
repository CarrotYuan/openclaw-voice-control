# OpenClaw Voice Control

`OpenClaw Voice Control` 是一个运行在 macOS 上的本地语音控制集成层，用来给 OpenClaw 提供语音唤起、语音识别、语音播报和后台常驻能力。

## 这个 Skill 是什么

这不是一个单纯的提示词技能，也不是一个只提供单一函数的小工具。

更准确地说，它是：

- 一个运行在 macOS 上的本地语音入口
- 一套唤醒词、录音、ASR、TTS、浮窗和后台常驻能力的整合层

换句话说，它让 OpenClaw 在本地机器上拥有一个类似 Siri 的语音入口。

## 这个 Skill 能提供什么

它当前提供这些能力：

- 唤醒词触发
- 本地麦克风录音
- 基于 FunASR / SenseVoice 的本地语音识别
- 将识别后的文本发送给本地 OpenClaw 智能体
- 使用 macOS TTS 播报回复
- 可选浮窗 UI
- 基于 `launchd` 的后台常驻
- 用户登录后的自动启动

## 平台范围

当前只支持：

- macOS

## 这个 Skill 不包含什么

公开仓库不会附带以下内容：

- `.env`
- 真实的 OpenClaw token
- 真实的 `.ppn` 唤醒词文件
- SenseVoice 模型文件
- VAD 模型文件
- 私有 OpenClaw 运行环境

也就是说，这个 Skill 可以从源码安装，但仍然依赖用户自己准备本地资源和密钥。

## 用户自己需要准备什么

在真正跑起来之前，用户仍然需要自己准备：

- Python 3.11 或更高版本
- 一个正在运行的本地 OpenClaw 服务
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- 一个真实可用的本地 `.ppn` 唤醒词文件
- 本地 SenseVoice 模型目录
- 本地 VAD 模型目录
- macOS 麦克风权限

## 推荐默认值

公开仓库已经提供了可直接使用的默认 OpenClaw 目标：

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

用户可以先用这组默认值跑通，再按需切换成自己的智能体。

## 安装思路

请先完整阅读 [README.md](../../README.md)。

当前项目的**主安装文档**是 [README.md](../../README.md)。
[README.zh-CN.md](../../README.zh-CN.md) 是中文辅助说明，便于阅读，但安装时应优先以主 README 为准。

## 直接安装路径

如果 AI 或用户需要一眼就能执行的最短安装路径，可以直接按下面顺序操作：

1. 克隆仓库
2. 创建并激活 `.venv`
3. 执行 `pip install -e .` 安装依赖
4. 从 `.env.example` 复制出 `.env`
5. 在 `.env` 中填好必填配置项
6. 将真实的 wakeword 文件和模型目录放到配置要求的位置
7. 先做前台验证
8. 再执行 `./scripts/deploy_macos.sh` 部署后台常驻

最短命令路径可以直接写成：

```bash
git clone <repo-url>
cd openclaw-voice-control
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# 在 .env 中填入真实值和本地资源路径
python -m openclaw_voice_control --config config/default.yaml --env-file .env
./scripts/deploy_macos.sh
```

标准流程是：

1. 克隆仓库
2. 创建 `.venv`
3. 安装依赖
4. 从 `.env.example` 复制出 `.env`
5. 填入真实密钥和本地资源路径
6. 先做前台验证
7. 再用 `./scripts/deploy_macos.sh` 部署后台常驻

更详细的步骤、排障和验证说明见：

- [README.md](../../README.md)
- [README.zh-CN.md](../../README.zh-CN.md)
- [docs/macos-install.md](../../docs/macos-install.md)
- [docs/fresh-clone-validation.md](../../docs/fresh-clone-validation.md)

## 日常维护方法

日常使用和维护时，主要看这几个脚本：

- 部署后台常驻：`./scripts/deploy_macos.sh`
- 重启已安装的后台服务：`./scripts/restart_service.sh`
- 卸载已安装的后台服务：`./scripts/uninstall_macos.sh`
- 检查本地安装和环境问题：`./scripts/doctor.sh`

如果用户更习惯在 Finder 中直接点击，也可以使用 `scripts/` 目录里的 `.command` 包装脚本。

## 背景架构为什么重要

当前仓库已经改成：

- `launchd -> host app -> shell script -> python`

这就是当前保留并推荐的标准后台部署方案。

`./scripts/deploy_macos.sh` 会自动构建所需的 host app。

## 主要配置项

最重要的配置项有：

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `OPENCLAW_AGENT_ID`
- `OPENCLAW_MODEL`
- `OPENCLAW_USER`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

以下两个变量仍然保留：

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

但它们只是排障用，不是当前推荐的主方案。

## 缺失配置项去哪里找

如果用户或 AI 发现缺少配置项、模型路径、wakeword 文件或凭据，不要凭空猜测。

请直接查看主安装文档 [README.md](../../README.md) 里的这三节：

- `What You Must Prepare Yourself`
- `Required Variables`
- `Where To Get Each Requirement`

这三节已经说明了：

- 哪些内容需要用户自己准备
- 各个 key、token 和本地资源从哪里获得
- `.ppn`、模型目录应该放在哪里
- 哪些值需要写入 `.env`
- 在部署后台前应如何做前台验证

这里再补几条最常用的来源说明：

- `OPENCLAW_TOKEN`：通常可以从本地 OpenClaw gateway 配置中获取，例如 `openclaw.json-gateway`
- `PICOVOICE_ACCESS_KEY`：在 [Picovoice](https://picovoice.ai/) 获取
- 本地 `.ppn` 唤醒词文件：在 [Picovoice](https://picovoice.ai/) 训练并下载

关于唤醒词还有一个很重要的实战提醒：

- 在 Picovoice 网站训练和测试模型时，一定要确认测试页面能明确看到“成功触发唤醒词”的提示
- 如果在网页测试阶段就没有成功触发，后续本地部署后也可能无法正常响应唤醒

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

## 相关文件

- [SKILL.md](./SKILL.md)
- [skill.json](../../skill.json)
- [docs/openclaw-skill.md](../../docs/openclaw-skill.md)
