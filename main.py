import os
import sys
import pyaudio
import numpy as np
import whisper
import time


class WakeWordAssistant:
    """
    使用 Whisper 持续监听 + 中文关键词匹配的语音助手。

    工作流程:
    1. 监听阶段：持续录制 3 秒音频，用 Whisper 快速识别
    2. 唤醒检测：检查识别结果中是否包含预设的中文唤醒词
    3. 命令识别：检测到唤醒词后，录制 10 秒音频做完整识别
    4. 停止命令：识别到 "stop" 或 "停止" 时退出
    """

    def __init__(self):
        # 音频参数
        self.rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk = 1024

        # 两个阶段的录制时长（秒）
        self.wake_duration = 3      # 监听阶段：持续识别
        self.command_duration = 10   # 命令阶段：完整识别

        # 中文唤醒词列表（用户可以添加更多）
        self.wake_words = ["小助手", "你好助手", "助手", "你好小助手", "嘿小助手"]

        # 运行状态
        self.is_running = True

        # 初始化模型和音频设备
        self.initialize_models()
        self.pyaudio = pyaudio.PyAudio()

    def initialize_models(self):
        print("Loading Whisper base model...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded!\n")

    def contains_wake_word(self, text):
        """检查文本中是否包含任何唤醒词。"""
        text_lower = text.lower()
        for w in self.wake_words:
            if w in text_lower:
                return True
        return False

    def contains_stop(self, text):
        """检查文本中是否包含停止词。"""
        text_lower = text.lower()
        return ("stop" in text_lower) or ("停止" in text_lower)

    def record_audio(self, duration_seconds):
        """录制指定时长的音频，返回 float32 numpy 数组。"""
        num_samples = int(self.rate * duration_seconds)
        print(f"  [录制中] {duration_seconds} 秒...")

        try:
            stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            frames = []
            for _ in range(0, int(self.rate / self.chunk * duration_seconds)):
                data = stream.read(self.chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            audio_data = b''.join(frames)
            audio = np.frombuffer(audio_data, dtype=np.int16)

            # 确保长度正确
            if len(audio) > num_samples:
                audio = audio[:num_samples]
            elif len(audio) < num_samples:
                audio = np.pad(audio, (0, num_samples - len(audio)), mode='constant')

            audio = audio.astype(np.float32) / 32768.0
            return audio

        except Exception as e:
            print(f"  音频录制错误: {e}")
            raise

    def transcribe(self, audio, description="识别"):
        """用 Whisper 识别音频，返回文本。"""
        print(f"  {description}中...")
        result = self.whisper_model.transcribe(
            audio,
            language='zh',
            fp16=False,
            verbose=False
        )
        text = result["text"].strip()
        return text

    def wake_detection_loop(self):
        """监听阶段：持续识别，检测唤醒词。"""
        print("=" * 60)
        print("语音助手已启动！")
        print("=" * 60)
        print(f"唤醒词: {', '.join(self.wake_words)}")
        print(f"说 'stop' 或 '停止' 可退出程序\n")

        while self.is_running:
            try:
                # 1. 录制 3 秒音频（监听阶段）
                print("[监听] 正在听...")
                audio = self.record_audio(self.wake_duration)

                # 2. Whisper 识别
                text = self.transcribe(audio, description="监听识别")

                if text:
                    print(f"  -> 听到: '{text}'")
                else:
                    print(f"  -> (静音/无语音)")

                # 3. 检查是否包含停止词（在监听阶段也可直接退出）
                if text and self.contains_stop(text):
                    print("\n[停止命令收到，正在退出...\n")
                    self.is_running = False
                    break

                # 4. 检查是否包含唤醒词
                if text and self.contains_wake_word(text):
                    print("\n>>> 唤醒词检测到！准备识别命令...\n")
                    self.command_mode()

            except KeyboardInterrupt:
                print("\n用户中断，正在退出...")
                self.is_running = False
                break
            except Exception as e:
                print(f"发生错误: {e}")
                import traceback
                traceback.print_exc()

    def command_mode(self):
        """命令识别阶段：录制更长的音频并完整识别。"""
        # 录制 10 秒命令
        print("[命令] 请说出你的命令...")
        audio = self.record_audio(self.command_duration)

        # Whisper 识别
        text = self.transcribe(audio, description="命令")

        print("\n" + "=" * 60)
        print(f"识别结果: {text}")
        print("=" * 60 + "\n")

        # 检查是否是停止命令
        if text and self.contains_stop(text):
            print("[停止] 收到停止命令，退出程序...\n")
            self.is_running = False
            return

        print("[返回] 回到监听模式...\n")

    def cleanup(self):
        """清理资源。"""
        self.pyaudio.terminate()

    def run(self):
        """启动语音助手主入口。"""
        try:
            self.wake_detection_loop()
        except KeyboardInterrupt:
            print("\n程序被中断。")
        finally:
            self.cleanup()
            print("\n语音助手已停止。")


if __name__ == "__main__":
    try:
        assistant = WakeWordAssistant()
        assistant.run()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
