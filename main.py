import os
import sys
import subprocess
import sounddevice as sd
import numpy as np
import openwakeword
import whisper
import time
import threading
from queue import Queue


class WakeWordAssistant:
    def __init__(self):
        self.rate = 16000
        self.channels = 1
        self.dtype = 'int16'
        self.chunk_size = 1280

        self.wakeword_model = None
        self.whisper_model = None

        self.audio_queue = Queue()
        self.detection_queue = Queue()

        self.is_running = False
        self.is_recording = False
        self.wakeword_detected = False
        self.recorded_audio = []

        self.initialize_models()

    def download_model_with_powershell(self, url, dest_path):
        try:
            ps_cmd = (
                "Invoke-WebRequest -Uri '" + url +
                "' -OutFile '" + dest_path + "' -UseBasicParsing"
            )
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            return True
        except Exception as e:
            print(f"  PowerShell download failed: {e}")
            return False

    def download_wakeword_models(self):
        models_dir = os.path.join(
            os.path.dirname(openwakeword.__file__),
            'resources', 'models'
        )
        os.makedirs(models_dir, exist_ok=True)

        model_info = [
            ('melspectrogram.onnx',
             'https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx'),
            ('embedding_model.onnx',
             'https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx'),
            ('hey_jarvis_v0.1.onnx',
             'https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_jarvis_v0.1.onnx'),
        ]

        all_exist = True
        for model_name, url in model_info:
            model_path = os.path.join(models_dir, model_name)
            if not os.path.exists(model_path):
                all_exist = False
                break

        if not all_exist:
            print("Downloading wakeword models (using PowerShell)...")
            for model_name, url in model_info:
                model_path = os.path.join(models_dir, model_name)
                if not os.path.exists(model_path):
                    print(f"  {model_name}...", end=" ")
                    if self.download_model_with_powershell(url, model_path):
                        print("OK")
                    else:
                        print("FAILED")
                        print(f"  Please download manually: {url}")
                        print(f"  And save to: {model_path}")
            print("Download step completed.")

    def initialize_models(self):
        print("Setting up wakeword models...")
        self.download_wakeword_models()

        print("Loading wakeword model (hey_jarvis, ONNX)...")
        self.wakeword_model = openwakeword.Model(
            wakeword_models=['hey_jarvis'],
            inference_framework='onnx'
        )
        print("Wakeword model loaded!")

        print("Loading Whisper model (base)...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper model loaded!")

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        audio_data = indata.flatten().astype(np.int16)
        self.audio_queue.put(audio_data)
        if not self.is_recording:
            self.detection_queue.put(audio_data)

    def wakeword_detection_thread(self):
        print("\nWakeword detection started...")
        print("Say 'hey jarvis' to activate voice recognition")
        print("Say 'stop' to exit the program\n")

        while self.is_running:
            try:
                audio_data = self.detection_queue.get(timeout=1)
                audio_float = audio_data.astype(np.float32) / 32768.0

                predictions = self.wakeword_model.predict(audio_float)

                for model_name, prob in predictions.items():
                    if prob > 0.5:
                        print(f"\n>> Wakeword detected! ({model_name}: {prob:.2f})")
                        self.wakeword_detected = True
                        self.start_recording()
                        break

            except Exception:
                continue

    def start_recording(self):
        print(">> Listening for command... (max 10 seconds)")
        self.is_recording = True
        self.recorded_audio = []

        recording_thread = threading.Thread(target=self.record_audio)
        recording_thread.start()

    def record_audio(self):
        max_duration = 10
        start_time = time.time()

        while self.is_recording and self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                self.recorded_audio.append(audio_data)

                if time.time() - start_time > max_duration:
                    print(">> Max duration reached, processing...")
                    self.stop_recording()

            except Exception:
                continue

    def stop_recording(self):
        self.is_recording = False

        if len(self.recorded_audio) > 0:
            self.process_audio()

        self.wakeword_detected = False
        print("\nWakeword detection resumed...")
        print("Say 'hey jarvis' to activate voice recognition\n")

    def process_audio(self):
        print(">> Processing audio with Whisper...")

        audio_data = np.concatenate(self.recorded_audio)
        audio_float = audio_data.astype(np.float32) / 32768.0

        result = self.whisper_model.transcribe(
            audio_float,
            language='zh',
            fp16=False
        )

        text = result['text'].strip()
        print(f"\n>> Recognition result: {text}")

        if 'stop' in text.lower() or '停止' in text:
            print(">> Stop command received, shutting down...")
            self.is_running = False

    def run(self):
        self.is_running = True

        detection_thread = threading.Thread(target=self.wakeword_detection_thread)
        detection_thread.start()

        try:
            with sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_size,
                callback=self.audio_callback
            ):
                while self.is_running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n>> Keyboard interrupt received...")
            self.is_running = False

        detection_thread.join()
        print(">> Assistant stopped.")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("OpenWakeWord + Whisper Voice Assistant")
        print("=" * 60)
        print()
        assistant = WakeWordAssistant()
        assistant.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
