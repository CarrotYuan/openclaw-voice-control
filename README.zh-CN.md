# OpenClaw Voice Control 中文说明

`OpenClaw Voice Control` 是一个运行在 macOS 上的本地语音控制伴侣，用来给 OpenClaw 提供一个像 Siri 一样可通过语音唤起的入口。

当前公开版的范围：

- 仅支持 macOS
- 默认使用中文 ASR
- 支持唤醒词、本地麦克风录音、本地 TTS
- 支持可选浮窗
- 支持基于 `launchd` 的后台常驻和自启动

## 项目能做什么

这个仓库可以让你：

- 说出唤醒词
- 录制本地语音请求
- 用 FunASR / SenseVoice 做语音识别
- 将文本请求发送给本地 OpenClaw 智能体
- 用 macOS TTS 播报回复
- 用浮窗展示状态和回复
- 将语音服务和浮窗安装为 LaunchAgent，用于后台常驻和自动启动

公开版默认连接 OpenClaw 的 `main` 智能体，方便用户先跑通再按需改成自己的智能体。

## 重要提醒：智能体安全约束

这个仓库提供的是一个本地语音入口，而不是只绑定某一个人的专属入口。

这意味着：

- 麦克风附近的任何人都可能触发唤醒词
- 语音入口连接到哪个 OpenClaw 智能体，就等于把那个智能体可访问的能力暴露到了语音触发面前

强烈建议你在目标智能体的提示词或系统指令中加入明确的安全约束，例如：

- 对高风险操作要求二次确认
- 不允许直接执行删除、付款、外发、改密、系统控制等危险行为
- 尽量使用最小权限原则开放工具
- 不要把过宽的自动化权限直接交给语音入口对应的智能体

一句话概括：

**请把语音入口视为一个共享触发面，并为它对应的智能体设计合理的权限边界。**

## 从零开始前，你需要自己准备什么

在一台全新的机器，或者一次全新克隆的环境里，仓库默认**不包含**下面这些东西：

- `.env`
- 真实的 `.ppn` 唤醒词文件
- SenseVoice 模型目录
- VAD 模型目录
- OpenClaw 本地服务
- 任何真实 token / key

你需要提前准备：

- 一台 macOS 机器
- Python 3.11 或更新版本
- 一个可访问的本地 OpenClaw 服务
- 有效的 `OPENCLAW_TOKEN`
- 有效的 `PICOVOICE_ACCESS_KEY`
- 一个真实的 Porcupine `.ppn` 唤醒词文件
- macOS 麦克风权限
- 以及按下文步骤下载本地 ASR 模型的能力

## 最少必须填写的环境变量

创建 `.env` 后，至少需要填写：

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

公开版可直接使用的默认值有：

- `OPENCLAW_AGENT_ID=main`
- `OPENCLAW_MODEL=openclaw:main`
- `OPENCLAW_USER=openclaw-voice-control`

以下变量仍然保留，但只是排障用，不是主方案：

- `VOICE_CONTROL_PYTHON_BIN`
- `VOICE_CONTROL_OVERLAY_PYTHON_BIN`

当前推荐的后台方案不是依赖解释器 override，而是项目自带的 host app 启动链路。

## 推荐的本地目录布局

建议在全新克隆后，把本地资源按下面的结构放置：

- 唤醒词：
  `assets/wakeword/your-model.ppn`
- SenseVoice：
  `models/SenseVoiceSmall`
- VAD：
  `models/fsmn-vad`

注意：

- `assets/wakeword/your-model.ppn` 只是占位路径
- 仓库本身**不提供**真实 `.ppn`

## 每个资源从哪里来

- `OPENCLAW_BASE_URL`
  使用你本地 OpenClaw 服务暴露出的地址
- `OPENCLAW_TOKEN`
  使用你本地 OpenClaw 环境中的有效 token。对这个项目，优先从 `~/.openclaw/openclaw.json` 的 `gateway` 配置获取，而不是从设备身份文件里读取
- `PICOVOICE_ACCESS_KEY`
  从 [Picovoice Console](https://picovoice.ai/) 获取
- `WAKEWORD_FILE`
  从 [Picovoice Console](https://picovoice.ai/) 获取或训练你自己的 `.ppn`
- `SENSEVOICE_MODEL_PATH`
  指向本地 SenseVoiceSmall 目录
- `SENSEVOICE_VAD_MODEL_PATH`
  指向本地 VAD 模型目录

## 完整部署流程

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd openclaw-voice-control
```

### 2. 创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

优先使用：

```bash
pip install -e .
```

也可以使用：

```bash
pip install -r requirements.txt
```

如果 `pip install -e .` 因为 PyPI SSL 校验失败，可以改用：

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

### 4. 创建 `.env`

```bash
cp .env.example .env
```

### 5. 填写 `.env`

至少填写：

- `OPENCLAW_BASE_URL`
- `OPENCLAW_TOKEN`
- `PICOVOICE_ACCESS_KEY`
- `WAKEWORD_FILE`
- `SENSEVOICE_MODEL_PATH`
- `SENSEVOICE_VAD_MODEL_PATH`

例如，可以按仓库内相对路径这样填写：

```bash
OPENCLAW_BASE_URL=http://127.0.0.1:18789/v1/chat/completions
OPENCLAW_TOKEN=replace_me
PICOVOICE_ACCESS_KEY=replace_me
WAKEWORD_FILE=assets/wakeword/your-model.ppn
SENSEVOICE_MODEL_PATH=models/SenseVoiceSmall
SENSEVOICE_VAD_MODEL_PATH=models/fsmn-vad
```

### 6. 准备唤醒词 `.ppn`

把你自己的真实 `.ppn` 文件放到 `.env` 指向的位置。

例如：

```text
assets/wakeword/your-model.ppn
```

注意：

- 仓库不自带真实 `.ppn`
- 如果你不明确拥有再分发权限，不要把自己的 `.ppn` 提交进 git
- 在 Picovoice 网站训练和测试唤醒词时，一定要确认测试页面明确显示“成功触发唤醒词”
- 如果网页测试阶段都没有成功触发，后续本地部署后也可能无法正常响应唤醒

### 7. 准备 SenseVoice 模型

一种可用方式：

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

### 8. 准备 VAD 模型

这里是一个容易踩坑的点。

配置里使用的是短别名：

```text
fsmn-vad
```

但它不是一个可以直接这样下载的 ModelScope repo id：

```bash
modelscope download --model fsmn-vad --local_dir models/fsmn-vad
```

正确做法是先通过 FunASR 解析并拉取：

```bash
./.venv/bin/python - <<'PY'
from funasr import AutoModel
AutoModel(model='fsmn-vad', disable_update=True)
PY
```

然后把解析出来的模型复制到：

```text
models/fsmn-vad
```

### 9. 先跑预检查

```bash
./scripts/doctor.sh
./.venv/bin/python scripts/list_audio_devices.py
./.venv/bin/python scripts/test_microphone.py --device -1 --seconds 3
```

理想结果：

- `doctor.sh` 通过
- `list_audio_devices.py` 能看到真实输入设备
- `test_microphone.py` 说话时 RMS 会变化

### 10. 前台启动主服务

```bash
python -m openclaw_voice_control --config config/default.yaml --env-file .env
```

正常启动时，日志通常会依次出现：

- `Loading ASR model...`
- `ASR model ready`
- `Initializing wakeword engine...`
- `Wakeword engine ready`
- `Entered idle listening loop`

### 11. 前台启动浮窗

在第二个终端执行：

```bash
python -m openclaw_voice_control.overlay_app --config config/default.yaml --env-file .env
```

浮窗在 `idle` 状态可能是隐藏的，这是正常行为。通常会在这些状态弹出：

- 检测到唤醒词
- 正在听
- 正在思考
- 正在回复

### 12. 验证前台完整链路

说出唤醒词和一个简短请求。

当前台完整链路真正跑通时，你通常会看到：

- 唤醒词触发
- 开始录音
- ASR 成功
- OpenClaw 返回回复
- TTS 成功播报

### 13. 部署后台 LaunchAgents

终端方式：

```bash
./scripts/deploy_macos.sh
```

双击方式：

- [deploy_macos.command](scripts/deploy_macos.command)

## 背景权限架构说明

这轮从全新克隆环境开始的验证里，最关键的问题不是安装，而是 macOS 的后台权限链路。

旧路径：

- `launchd -> shell -> bare python`

在部分机器上，这条路径下的麦克风权限行为不够稳定。

当前仓库已经改成：

- `launchd -> host app -> shell script -> python`

`deploy_macos.sh` 会自动构建 host app：

- `runtime/host_apps/OpenClawVoiceControlServiceHost.app`
- `runtime/host_apps/OpenClawVoiceControlOverlayHost.app`

随后由 LaunchAgent 指向这些 host app 的可执行文件。

这也是当前推荐的后台方案。

### 14. 验证后台常驻

部署后请验证：

- 服务是否保持在后台运行
- 麦克风是否真的可用
- 在不依赖前台终端的情况下，唤醒词是否还能触发
- 回复和浮窗是否正常

重要提醒：

不要在 deploy 之后因为“暂时还没响应”就立刻判断失败。

真实机器验证表明，冷启动时后台服务可能仍在：

- `Loading ASR model...`
- `Initializing wakeword engine...`

请等日志到达：

- `Wakeword engine ready`
- `Entered idle listening loop`

再判断后台是否真的没起来。

### 15. 验证自启动

后台部署成功后，再继续验证：

- 注销再登录，或重启用户会话
- 服务和浮窗是否自动拉起
- 唤醒词是否仍能成功触发

### 16. 重启或卸载

重启：

```bash
./scripts/restart_service.sh
```

双击：

- [restart_service.command](scripts/restart_service.command)

卸载：

```bash
./scripts/uninstall_macos.sh
```

双击：

- [uninstall_macos.command](scripts/uninstall_macos.command)

当前 `uninstall_macos.sh` 不只是删除 plist，还会一并清理：

- LaunchAgent 注册记录
- `runtime/host_apps` 下生成的 host app
- 匹配到的 host app 进程
- 匹配到的前台测试 Python 进程

这是因为真实测试中发现，如果前台测试进程残留，很容易误以为“卸载失败”。

## 重要配置位置

- [.env.example](./.env.example)
- [config/default.yaml](./config/default.yaml)
- [src/openclaw_voice_control/config.py](./src/openclaw_voice_control/config.py)
- [requirements.txt](./requirements.txt)

通常来说：

- `.env` 负责密钥、令牌和路径
- `config/default.yaml` 负责音频、ASR、TTS、wakeword、overlay 默认值
- `config.py` 负责配置合并逻辑

## TTS 配置

项目目前使用 macOS `say` 做播报。

主要看：

- [config/default.yaml](./config/default.yaml) 中的 `tts:`
- [tts.py](./src/openclaw_voice_control/tts.py)

常用字段包括：

- `tts.voice`
- `tts.wake_ack`
- `tts.followup_beep_enabled`
- `tts.followup_beep_sound`
- `tts.record_done_beep_enabled`
- `tts.record_done_sound`
- `tts.no_speech_beep_enabled`
- `tts.no_speech_sound`
- `tts.post_reply_delay`

例如，切换播报音色：

```yaml
tts:
  engine: macos_say
  voice: Tingting
```

查看本机可用音色：

```bash
say -v '?'
```

## 常见问题与解决方法

### 全新克隆后缺少运行资源

这是预期行为。公开仓库不会附带：

- `.env`
- 真实 `.ppn`
- `models/SenseVoiceSmall`
- `models/fsmn-vad`

需要你自己补齐。

### `.ppn` 示例路径看起来像真实文件

公开仓库现在使用：

```text
assets/wakeword/your-model.ppn
```

它只是占位，不是仓库自带资产。

### `pip install -e .` 因 SSL 失败

使用：

```bash
./.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

### `fsmn-vad` 不能直接下载

这是正常的，因为它是 FunASR 的别名，不是直接的 ModelScope repo id。

请先用上面那段 `AutoModel(model='fsmn-vad')` 的方式完成解析。

### ASR 能启动，但识别结果是明显乱码

如果唤醒词已经正常触发，服务也进入了 listening，但识别结果看起来像多语种碎片、随机 token 或明显乱码，请检查本地 SenseVoice 模型目录是否真的完整。

尤其要确认：

- `models/SenseVoiceSmall`

或者 `SENSEVOICE_MODEL_PATH` 指向的目录里，是否仍然包含核心权重文件：

- `model.pt`

有些情况下，目录本身虽然存在，但如果缺少 `model.pt` 或其他关键文件，ASR 仍可能“看起来能启动”，但最终输出会是异常乱码。

如果有怀疑，建议重新下载或重新复制完整模型目录：

```bash
./.venv/bin/modelscope download --model iic/SenseVoiceSmall --local_dir models/SenseVoiceSmall
```

不要只因为“目录存在”就认定模型可用，关键文件必须完整。

### 前台能启动不代表端到端一定成功

需要分开验证：

- 前台启动
- 前台完整交互
- 后台部署
- 后台唤醒与回复
- 自启动

### macOS 背景权限问题

这个是这轮验证中最核心的问题。

最终解决方法不是继续沿用旧的 bare Python 启动链，而是改成：

- `launchd -> host app -> shell script -> python`

这套方案已经在真实机器上验证通过：

- 唤醒可用
- 回复可用
- 后台常驻可用
- 自启动可用

### uninstall 后看起来还有服务残留

真实测试发现，原因可能不是 LaunchAgent 没卸载，而是：

- 前台测试 Python 进程还活着
- 生成的 host app 还留在 `runtime/host_apps`

当前脚本已经针对这两类内容做了清理。

## 当前限制

- 仅支持 macOS
- 默认中文 ASR
- 仓库不处理唤醒词资产再分发
- 用户仍需自己准备 `.ppn`、OpenClaw 凭据和 ASR 模型目录

## 相关文档

- [README.md](./README.md)
- [docs/macos-install.md](./docs/macos-install.md)
- [docs/fresh-clone-validation.md](./docs/fresh-clone-validation.md)
- [docs/same-machine-test.md](./docs/same-machine-test.md)
- [docs/architecture.md](./docs/architecture.md)
- [docs/release-checklist.md](./docs/release-checklist.md)

## License

本仓库使用 [MIT License](./LICENSE)。
