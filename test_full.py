import whisper
import pyaudio
import numpy as np

print("=" * 60)
print("Whisper 中文语音助手 - 集成测试")
print("=" * 60)
print()

print("[1/3] 加载 Whisper base 模型...")
w = whisper.load_model('base')
print("      OK - Whisper 模型加载成功")

print("[2/3] 测试语音识别...")
audio = np.zeros(16000, dtype=np.float32)
result = w.transcribe(audio, language='zh', fp16=False)
text = result["text"]
print(f"      OK - 识别结果: '{text}'")

print("[3/3] 测试 PyAudio 音频设备...")
pa = pyaudio.PyAudio()
device_count = pa.get_device_count()
print(f"      OK - 发现 {device_count} 个音频设备")

default_input = pa.get_default_input_device_info()
print(f"           默认输入设备: {default_input.get('name', '未知')}")
print(f"           采样率: {default_input.get('defaultSampleRate', '未知')}")

pa.terminate()
print()
print("=" * 60)
print("所有测试通过！")
print("=" * 60)
print()
print("唤醒词: 小助手, 你好助手, 助手, 你好小助手, 嘿小助手")
print("运行 'python main.py' 启动语音助手")
print("说任意唤醒词即可触发命令识别")
print("说 'stop' 或 '停止' 退出程序")
