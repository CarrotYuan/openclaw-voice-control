---
name: openclaw-voice-control
description: Local macOS voice-control integration for OpenClaw. Use when setting up, deploying, troubleshooting, or operating wakeword-triggered voice access to a local OpenClaw agent with ASR, TTS, overlay UI, and launchd background support.
---

# OpenClaw Voice Control

`OpenClaw Voice Control` 是一个运行在 macOS 上的本地语音控制集成层，用来给 OpenClaw 提供语音唤起、语音识别、语音播报和后台常驻能力。

项目仓库来源：

- GitHub：[CarrotYuan/openclaw-voice-control](https://github.com/CarrotYuan/openclaw-voice-control)

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

当这个 skill 被安装到 OpenClaw 后，请默认从**当前对话智能体所加载的 skill 目录**开始操作。

对于由 OpenClaw 驱动的部署，项目应部署在**当前对话智能体所加载的 skill 目录**中。

开始任何部署动作之前，先遵守这几条：

- 先完整阅读当前这份 `SKILL.md`
- 优先使用本 skill 明确给出的 GitHub 仓库来源
- 部署工作保持在当前已安装的 skill 工作目录内
- 不要擅自切换到别的本地克隆目录或已经配好的旧环境

如果需要项目仓库内容，应先把项目仓库内容同步到当前已安装的 skill 工作目录，再去阅读其中的 `README.md`。

克隆后的项目仓库中：

- `README.md` 是**主安装文档**
- `README.zh-CN.md` 是中文辅助说明

## 直接安装路径

如果 AI 或用户需要一眼就能执行的最短安装路径，可以直接按下面顺序操作：

1. 从当前已安装的 skill 目录开始，把项目仓库内容放入当前已安装的 skill 工作目录
2. 创建并激活 `.venv`
3. 执行 `pip install -e .` 安装依赖
4. 从 `.env.example` 复制出 `.env`
5. 在 `.env` 中填好必填配置项
6. 将真实的 wakeword 文件和模型目录放到配置要求的位置
7. 先做前台验证
8. 询问用户是否需要开启后台常驻与自启动
9. 如果需要，再执行 `./scripts/deploy_macos.sh`
10. 如果不需要，则停在前台运行方案即可

最短命令路径可以直接写成：

```bash
# 从当前对话智能体所加载的 skill 目录开始
git init
git remote add origin https://github.com/CarrotYuan/openclaw-voice-control.git
git fetch --depth 1 origin main
git checkout -B main FETCH_HEAD
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# 在 .env 中填入真实值和本地资源路径
python -m openclaw_voice_control --config config/default.yaml --env-file .env
# 先询问用户是否需要后台常驻与自启动
# 如果需要：
./scripts/deploy_macos.sh
```

## 执行规则

使用这个 skill 时，请严格遵守下面这些规则：

1. **优先使用这里声明的 GitHub 仓库**
   - 从 `https://github.com/CarrotYuan/openclaw-voice-control.git` 开始
   - 不要因为看到别的相似仓库就自行替换
   - 部署位置固定为当前对话智能体所加载的 skill 目录，不要切到任意其他目录

2. **不要擅自回退到本地现成仓库**
   - 如果 GitHub 拉取失败，要先明确报告失败原因
   - 如果发现本地已有克隆，必须先征得用户同意，才能改用它

3. **不要擅自复用旧环境**
   - 不要默认复用现成 `.venv`、本地模型缓存、旧 `.env` 或私有运行环境
   - 如果复用缓存可能节省时间，也要先说明并征求同意

4. **不要编造缺失值**
   - 如果缺少 `.ppn`、token、模型路径或其他关键配置，就停下来，并指向文档中说明的获取位置
   - 写 `.env` 时必须使用项目要求的真实变量名，尤其是 `OPENCLAW_TOKEN`

5. **谨慎处理敏感信息**
   - 不要把真实 token 或 key 明文回显到对话里，除非用户明确要求查看
   - 对这个项目，OpenClaw token 只从 `~/.openclaw/openclaw.json` 的 `gateway` 配置获取
   - 不要使用 `~/.openclaw/identity/device-auth.json` 作为这个项目的 token 来源

6. **优先走 fresh-clone 可复现路径**
   - 无论是测试还是部署，都优先采用一个新用户从全新克隆开始也能复现的路径

7. **不要默认强行开启后台常驻**
   - 当前台验证成功后，先询问用户是否需要后台常驻与自启动
   - 如果用户只是想本地试跑或手动使用，就停在前台方案
   - 只有当用户明确需要后台常驻或开机/唤醒后自动可用时，才执行 `./scripts/deploy_macos.sh`

标准流程是：

1. 从 GitHub 克隆仓库
2. 创建 `.venv`
3. 安装依赖
4. 从 `.env.example` 复制出 `.env`
5. 填入真实密钥和本地资源路径
6. 先做前台验证
7. 再用 `./scripts/deploy_macos.sh` 部署后台常驻

更详细的步骤、排障和验证说明见：

- 克隆后的仓库中的 `README.md`
- 克隆后的仓库中的 `README.zh-CN.md`
- 克隆后的仓库中的 `docs/macos-install.md`
- 克隆后的仓库中的 `docs/fresh-clone-validation.md`

## 日常维护方法

日常使用和维护时，主要看这几个脚本：

- 部署后台常驻：`./scripts/deploy_macos.sh`
- 重启已安装的后台服务：`./scripts/restart_service.sh`
- 卸载已安装的后台服务：`./scripts/uninstall_macos.sh`
- 检查本地安装和环境问题：`./scripts/doctor.sh`

如果用户更习惯在 Finder 中直接点击，也可以使用 `scripts/` 目录里的 `.command` 包装脚本。

## 部署分支选择

当前台链路已经跑通后，要明确区分下面两种部署目标：

- **仅前台 / 手动使用**
  - 用户只想在需要时手动启动语音助手
  - 这种情况下，完成前台验证后就可以停止
  - 不需要开启后台常驻，也不需要开启自启动

- **后台常驻 + 自启动**
  - 用户希望语音助手在后台常驻，并在登录、唤醒后自动可用
  - 这种情况下，再继续执行 `./scripts/deploy_macos.sh`

如果用户没有明确表达偏好，就先问，不要自己替用户决定。

## 两种关闭意图

把“关闭语音”类请求只区分成下面两种用户意图：

- **临时关闭语音功能**
  - 含义：先暂停语音功能，但后面仍可重新开启
  - 对这种意图，不要删除 skill 文件夹
  - 如果当前是前台运行，就停止当前运行中的进程
  - 如果当前是后台常驻，就停止已部署的后台运行时，但不要把它当作永久删除

- **直接删除 skill**
  - 含义：删除 skill 文件夹本身
  - 后面如果还要再用，需要重新部署或重新安装
  - 只有当用户明确要求彻底删除这个 skill 本身时，才这样做

如果用户说的是这类模糊表达：

- “关掉它”
- “关闭语音”
- “停止语音服务”
- “先别让它运行了”

那么不要自己猜，先追问一句：

- 你是想临时关闭语音功能，还是想彻底删除这个 skill？

## 背景架构为什么重要

当前保留并推荐的后台方案是：

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

请在克隆项目仓库后，直接查看其中 `README.md` 里的这三节：

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

- `OPENCLAW_TOKEN`：从 `~/.openclaw/openclaw.json` 的 `gateway` 配置获取
- `PICOVOICE_ACCESS_KEY`：在 [Picovoice](https://picovoice.ai/) 获取
- 本地 `.ppn` 唤醒词文件：在 [Picovoice](https://picovoice.ai/) 训练并下载
- 如果 GitHub 拉取失败，先报告失败，不要直接切换到不相关的本地目录

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
- 克隆后的仓库中的 `README.md`
- 克隆后的仓库中的 `README.zh-CN.md`
