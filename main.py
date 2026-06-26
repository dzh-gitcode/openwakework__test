import os
import sys
import pyaudio
import numpy as np
import whisper
import time
import pyttsx3


class WakeWordAssistant:
    """
    使用 Whisper 持续监听 + 中文关键词匹配的语音助手。

    工作流程:
    1. 监听阶段：持续录制 3 秒音频，用 Whisper 快速识别
    2. 唤醒检测：检查识别结果中是否包含预设的中文唤醒词
    3. 命令识别：检测到唤醒词后，录制 10 秒音频做完整识别
    4. 语音播报：识别结果用 TTS 语音播报
    5. 停止命令：识别到 "stop" 或 "停止" 时退出
    """

    def __init__(self):
        # 麦克风原生采样率（检测后设置）
        self.device_rate = 44100
        
        # Whisper 需要的采样率
        self.target_rate = 16000
        
        # 音频参数
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk = 1024

        # 两个阶段的录制时长（秒）
        self.wake_duration = 3
        self.command_duration = 10

        # 中文唤醒词列表
        self.wake_words = ["你好", "小助手", "你好助手", "助手", "你好小助手", "嘿小助手"]

        # 运行状态
        self.is_running = True

        # TTS 配置（每次播报时重新创建引擎）
        self.chinese_voice_id = None
        self.tts_available = True

        # 初始化模型、音频设备和 TTS
        self.initialize_models()
        self.initialize_tts()
        self.pyaudio = pyaudio.PyAudio()
        self.detect_device_info()

    def initialize_models(self):
        print("Loading Whisper base model...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded!\n")

    def initialize_tts(self):
        """检测可用语音，保存中文语音 ID。"""
        print("初始化 TTS 语音合成引擎...")
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            for voice in voices:
                voice_name = voice.name.lower()
                if 'chinese' in voice_name or '中文' in voice_name or 'zh' in voice_name:
                    self.chinese_voice_id = voice.id
                    print(f"使用中文语音: {voice.name}")
                    break
            
            if not self.chinese_voice_id:
                print("未找到中文语音，使用默认语音")
            
            engine.stop()
            engine = None
            
            print("TTS 初始化完成！\n")
            
        except Exception as e:
            print(f"TTS 初始化失败: {e}")
            print("语音播报功能将不可用\n")
            self.tts_available = False

    def speak(self, text):
        """将文本转换为语音播放（每次创建新引擎实例）。"""
        if not self.tts_available:
            print(f"[TTS不可用] {text}")
            return
        
        try:
            print(f"🔊 播报: {text}")
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            
            if self.chinese_voice_id:
                engine.setProperty('voice', self.chinese_voice_id)
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
        except Exception as e:
            print(f"语音播报失败: {e}")

    def detect_device_info(self):
        """检测麦克风设备信息并设置最优采样率。"""
        device_count = self.pyaudio.get_device_count()
        default_input_idx = self.pyaudio.get_default_input_device_info()["index"]
        
        for i in range(device_count):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if i == default_input_idx:
                print(f"使用麦克风: {device_info.get('name', '未知')}")
                self.device_rate = int(device_info.get('defaultSampleRate', 44100))
                print(f"设备采样率: {self.device_rate} Hz")
                print(f"目标采样率: {self.target_rate} Hz")
                
                # 检查是否支持 16000Hz
                supported_rates = [8000, 16000, 22050, 32000, 44100, 48000]
                if self.target_rate in supported_rates:
                    try:
                        # 尝试打开 16000Hz 的流
                        test_stream = self.pyaudio.open(
                            format=self.format,
                            channels=self.channels,
                            rate=self.target_rate,
                            input=True,
                            input_device_index=default_input_idx,
                            frames_per_buffer=self.chunk
                        )
                        test_stream.close()
                        print("麦克风支持 16000Hz，直接使用该采样率")
                        self.device_rate = self.target_rate
                    except:
                        print("麦克风不支持 16000Hz，将使用设备采样率录制后转换")
                break

    def resample_audio(self, audio, original_rate, target_rate):
        """使用 numpy 实现高质量采样率转换。"""
        if original_rate == target_rate:
            return audio
        
        duration = len(audio) / original_rate
        num_samples = int(duration * target_rate)
        
        old_indices = np.arange(len(audio))
        new_indices = np.linspace(0, len(audio) - 1, num_samples)
        
        return np.interp(new_indices, old_indices, audio)

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
        """录制指定时长的音频，返回 float32 numpy 数组（16000Hz）。"""
        num_samples = int(self.device_rate * duration_seconds)
        print(f"  [录制中] {duration_seconds} 秒...")

        try:
            stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.device_rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            frames = []
            for _ in range(0, int(self.device_rate / self.chunk * duration_seconds)):
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

            # 转换为 float32
            audio = audio.astype(np.float32) / 32768.0
            
            # 采样率转换（如果需要）
            if self.device_rate != self.target_rate:
                audio = self.resample_audio(audio, self.device_rate, self.target_rate)

            return audio

        except Exception as e:
            print(f"  音频录制错误: {e}")
            import traceback
            traceback.print_exc()
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

                # 3. 检查是否包含停止词
                if text and self.contains_stop(text):
                    print("\n[停止命令收到，正在退出...\n")
                    self.speak("再见，语音助手已停止")
                    self.is_running = False
                    break

                # 4. 检查是否包含唤醒词
                if text and self.contains_wake_word(text):
                    print("\n>>> 唤醒词检测到！准备识别命令...\n")
                    self.speak("我在")
                    self.command_mode()

            except KeyboardInterrupt:
                print("\n用户中断，正在退出...")
                self.speak("再见")
                self.is_running = False
                break
            except Exception as e:
                print(f"发生错误: {e}")
                import traceback
                traceback.print_exc()

    def command_mode(self):
        """命令识别阶段：录制更长的音频并完整识别。"""
        print("[命令] 请说出你的命令...")
        audio = self.record_audio(self.command_duration)

        text = self.transcribe(audio, description="命令")

        print("\n" + "=" * 60)
        print(f"识别结果: {text}")
        print("=" * 60 + "\n")

        # 播报识别结果（移除唤醒词，避免重复）
        if text:
            clean_text = text
            for wake_word in self.wake_words:
                clean_text = clean_text.replace(wake_word, "")
            clean_text = clean_text.strip()
            
            if clean_text:
                self.speak(f"收到，{clean_text}")
            else:
                self.speak("收到")

        if text and self.contains_stop(text):
            print("[停止] 收到停止命令，退出程序...\n")
            self.speak("再见，语音助手已停止")
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