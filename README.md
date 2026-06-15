# OpenWakeWord + Whisper 语音唤醒助手

一个基于 openWakeWord + Whisper 的实时语音唤醒与识别项目，可以通过麦克风检测唤醒词并识别语音内容。

## 功能特性

- **唤醒词检测**: 使用 openWakeWord 检测 "hey jarvis" 唤醒词
- **语音识别**: 使用 Whisper (base 模型) 进行中文/英文语音转文字
- **实时处理**: 基于 sounddevice 的实时音频流处理
- **停止命令**: 识别到 "stop" 或 "停止" 时自动退出程序

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

在 `pytorch_env` 环境中安装额外的包：

```bash
pip install openwakeword sounddevice soundfile openai-whisper tflite-runtime
```

或者使用项目中的 `requirements.txt`（如果需要创建新环境）：

```bash
pip install -r requirements.txt
```

### 3. 运行测试（可选，验证环境）

```bash
python test_full.py
```

预期输出：

```
============================================================
OpenWakeWord + Whisper Voice Assistant - Integration Test
============================================================

[1/4] Loading wakeword model (hey_jarvis, ONNX)...
      OK - wakeword model loaded
[2/4] Testing wakeword prediction...
      OK - predictions: {'hey_jarvis': 0.0}
[3/4] Loading whisper model (base)...
      OK - whisper model loaded
[4/4] Testing transcription...
      OK - transcription result: ''

============================================================
ALL TESTS PASSED!
Project is ready to use.
============================================================
```

### 4. 运行主程序

```bash
python main.py
```

## 使用说明

1. 启动程序后，会先加载 openWakeWord 和 Whisper 模型
2. 等待提示 "Wakeword detection started..."
3. 对着麦克风说 **"hey jarvis"** 来唤醒语音识别
4. 唤醒词检测到后，程序会录制最多 10 秒的语音
5. 录制完成后，Whisper 会将语音转成文字并显示
6. 说 **"stop"** 或 **"停止"** 可以退出程序
7. 随时按 `Ctrl+C` 也可以退出

## 模型文件

### openWakeWord 模型
- 路径: `<python>/site-packages/openwakeword/resources/models/`
- 需要的文件:
  - `melspectrogram.onnx` (音频特征提取)
  - `embedding_model.onnx` (嵌入模型)
  - `hey_jarvis_v0.1.onnx` (唤醒词检测模型)
- 首次运行时，程序会自动使用 PowerShell 下载模型（约 30-60MB）

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
- 块大小: 1280 样本 (~80ms)

### 唤醒词检测
- 使用 ONNX 推理框架（比 tflite 在 Windows 上更稳定）
- 检测阈值: 0.5 (predictions['hey_jarvis'] > 0.5 时触发)
- 模型来源: openWakeWord 官方预训练模型

### 语音识别
- Whisper base 模型 (~139MB)
- 语言: 中文 (zh)
- 禁用 fp16 (在 CPU 上运行更稳定)

## 常见问题

### Q1: 麦克风没有声音或权限不足？
**A**: 
- Windows: 设置 -> 隐私 -> 麦克风，确保已启用
- macOS: 系统偏好设置 -> 安全性与隐私 -> 麦克风
- 运行 `python test_audio.py` 检查设备

### Q2: 唤醒词检测不到？
**A**: 
- 确保环境安静
- 清晰地说 "hey jarvis"
- 检查麦克风是否工作正常
- 可以尝试降低检测阈值（在 `main.py` 中修改 `prob > 0.5`）

### Q3: Whisper 模型下载失败？
**A**: 
- 使用 `download_whisper.ps1` 脚本手动下载
- 或手动从 URL 下载，保存到 `%USERPROFILE%\.cache\whisper\base.pt`

### Q4: 第一次运行很慢？
**A**: 
- 首次运行需要下载模型文件（~200MB 总大小）
- 后续运行模型会从缓存加载，速度很快
- Whisper 模型加载约 1-2 秒

### Q5: 可以用其他唤醒词吗？
**A**: 
- openWakeWord 提供多种预训练模型（alexa, hey_mycroft 等）
- 修改 `main.py` 中的 `wakeword_models=['hey_jarvis']`
- 可从 https://github.com/dscripka/openWakeWord 查看完整列表

### Q6: 可以使用更大的 Whisper 模型吗？
**A**: 
- 修改 `main.py` 中 `whisper.load_model("base")` 为 "small", "medium", "large" 等
- 但更大的模型需要更多内存和计算时间
- 建议: base (139MB) -> small (461MB) -> medium (1.5GB) -> large (2.9GB)

## 依赖列表

主要依赖包及其版本:
- `torch`: 2.0.0 (已在 pytorch_env 中)
- `openwakeword`: >= 0.6.0
- `openai-whisper`: >= 20231117
- `sounddevice`: >= 0.5.0
- `soundfile`: >= 0.13.0
- `onnxruntime`: 自动安装（openwakeword 依赖）
- `tflite-runtime`: 可选（用于 tflite 格式模型）

## License

MIT License - 欢迎自由使用和修改。
