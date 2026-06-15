# OpenWakeWord + Whisper 语音唤醒助手

一个基于 **Whisper 持续监听 + 中文关键词匹配** 的实时语音识别项目。

无需训练任何模型！中文唤醒词直接用 Whisper 识别即可工作。

## 功能特性

- **中文唤醒词**: 支持 "小助手"、"你好助手"、"助手"、"你好小助手"、"嘿小助手" 等中文唤醒词
- **语音识别**: 使用 Whisper base 模型进行中文/英文语音转文字
- **停止命令**: 识别到 "stop" 或 "停止" 时自动退出
- **两阶段设计**:
  - 监听阶段：每 3 秒识别一次，检测是否包含唤醒词
  - 命令阶段：检测到唤醒词后，录制 10 秒做完整识别

## 为什么用方案 B？

相比 openWakeWord + Whisper 的方案：

| 对比项 | openWakeWord 方案 | Whisper 持续监听（当前方案） |
|--------|------------------|----------------------------|
| 中文唤醒词 | ❌ 需要自己训练 | ✅ 直接支持，无需训练 |
| 模型数量 | 2 个模型 | 1 个模型 |
| 实时性 | ⚡ 快（小模型） | 🐢 稍慢（Whisper 更大） |
| 功耗 | 低 | 较高 |
| 灵活性 | 固定唤醒词 | 可随时修改唤醒词 |

**适用场景**：在电脑/服务器上运行，对功耗要求不高的应用场景。

## 环境要求

- Python 3.8+
- Windows/macOS/Linux
- 可用的麦克风设备
- 至少 4GB 内存

## 项目结构

```
.
├── main.py                 # 主程序
├── test_full.py            # 集成测试脚本
├── test_whisper.py         # Whisper 测试脚本
├── test_audio.py           # 音频设备测试脚本
├── download_whisper.ps1    # Whisper 模型下载脚本 (PowerShell)
├── requirements.txt        # Python 依赖列表
└── README.md               # 本文件
```

## 快速开始

### 1. 激活 Conda 环境

本项目使用现有的 `pytorch_env` Conda 环境（已安装 torch 2.0.0）：

```bash
# Windows (PowerShell)
conda activate pytorch_env
```

### 2. 安装依赖

```bash
pip install openai-whisper sounddevice soundfile
```

或者：

```bash
pip install -r requirements.txt
```

### 3. 运行测试（可选）

```bash
python test_full.py
```

预期输出：

```
============================================================
Whisper 中文语音助手 - 集成测试
============================================================

[1/3] 加载 Whisper base 模型...
      OK - Whisper 模型加载成功
[2/3] 测试语音识别...
      OK - 识别结果: ''
[3/3] 测试音频设备...
      OK - 发现 5 个音频设备

============================================================
所有测试通过！
============================================================
```

### 4. 运行主程序

```bash
python main.py
```

## 使用说明

1. 启动程序后，会加载 Whisper 模型（约 1-2 秒）
2. 程序进入**监听阶段**，每 3 秒录制并识别一次
3. 对着麦克风说任一**中文唤醒词**（"小助手"、"你好助手" 等）
4. 检测到唤醒词后，进入**命令阶段**，会提示你说话
5. 说出你的命令，最多 10 秒，识别结果会显示出来
6. 然后自动回到监听阶段
7. 说 **"停止"** 或 **"stop"**、或按 `Ctrl+C` 可以退出程序

## 模型文件

### Whisper 模型
- 路径: `%USERPROFILE%\.cache\whisper\`
- 需要的文件: `base.pt` (~139MB)
- 首次加载时 whisper 会自动下载（约 58 秒，取决于网络速度）
- 如果自动下载失败:
  - 运行 `download_whisper.ps1` 手动下载
  - 或从 https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt 下载

## 技术细节

### 音频参数
- 采样率: 16000 Hz
- 通道: 单声道
- 采样精度: 16-bit (int16)

### 两阶段工作流程

```
[监听阶段]                  [命令阶段]
   ┌─────────────────┐          ┌─────────────────┐
   │ 录制 3 秒音频    │ ─触发→  │ 录制 10 秒音频  │
   │ Whisper 识别     │          │ Whisper 识别     │
   │ 检查唤醒词       │          │ 输出完整识别结果 │
   │ 无唤醒词 → 循环  │          │ 回到监听阶段     │
   └─────────────────┘          └─────────────────┘
```

### 唤醒词

默认的中文唤醒词列表（可在 `main.py` 中修改 `self.wake_words`）：

```python
self.wake_words = ["小助手", "你好助手", "助手", "你好小助手", "嘿小助手"]
```

你可以随意添加更多中文唤醒词，无需重新训练任何模型！

### 语音识别
- Whisper base 模型 (~139MB)
- 语言: 中文 (zh)
- 禁用 fp16 (在 CPU 上运行更稳定)

## 自定义配置

在 `main.py` 的 `__init__` 方法中可修改：

| 配置项 | 变量名 | 默认值 | 说明 |
|-------|--------|--------|------|
| 监听时长 | `self.wake_duration` | 3 秒 | 监听阶段每次录音时长 |
| 命令时长 | `self.command_duration` | 10 秒 | 命令阶段录音时长 |
| 唤醒词列表 | `self.wake_words` | 见上 | 添加/修改唤醒词 |

## 常见问题

### Q1: 唤醒词识别不到？
**A**:
- 确保环境安静
- 清晰地说出中文唤醒词，如 "小助手"
- 可以尝试增加唤醒词数量（在 `self.wake_words` 中添加）
- 监听阶段只有 3 秒，确保在这 3 秒内说出唤醒词

### Q2: 可以调快识别速度吗？
**A**:
- 减小 `self.wake_duration`（例如从 3 秒改成 2 秒）
- 改成 `whisper.load_model("tiny")` 使用更小的模型，但中文识别率会下降
- 如果你有 NVIDIA GPU，去掉 `fp16=False` 可以用 GPU 加速

### Q3: 可以使用更大的模型提升识别率吗？
**A**: 可以。修改 `whisper.load_model("base")`：
- `tiny` (75MB) - 最快，识别率较低
- `base` (139MB) - **默认**，推荐
- `small` (461MB) - 更好的识别率
- `medium` (1.5GB) - 很好，但较慢
- `large` (2.9GB) - 最好，很慢

### Q4: Whisper 模型下载失败？
**A**:
- 使用 `download_whisper.ps1` 脚本手动下载
- 或从官方 URL 下载保存到 `%USERPROFILE%\.cache\whisper\base.pt`

### Q5: 可以同时用英文唤醒词吗？
**A**: 当然可以！直接把英文词加入 `self.wake_words`，例如：
```python
self.wake_words = ["小助手", "你好助手", "hey jarvis", "ok google", "alexa"]
```

### Q6: 麦克风没有声音或权限不足？
**A**:
- Windows: 设置 -> 隐私 -> 麦克风，确保已启用
- 运行 `python test_audio.py` 检查设备

## 依赖列表

主要依赖包及其版本:
- `torch`: 2.0.0 (已在 pytorch_env 中)
- `openai-whisper`: >= 20231117
- `sounddevice`: >= 0.5.0
- `soundfile`: >= 0.13.0
- `numpy`: >= 1.21.0

## License

MIT License - 欢迎自由使用和修改。
