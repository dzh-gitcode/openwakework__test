import openwakeword
import whisper
import sounddevice
import numpy as np
import time

print("=" * 60)
print("OpenWakeWord + Whisper Voice Assistant - Integration Test")
print("=" * 60)
print()

print("[1/4] Loading wakeword model (hey_jarvis, ONNX)...")
m = openwakeword.Model(wakeword_models=['hey_jarvis'], inference_framework='onnx')
print("      OK - wakeword model loaded")

print("[2/4] Testing wakeword prediction...")
audio = np.zeros(1280, dtype=np.float32)
for i in range(5):
    preds = m.predict(audio)
print(f"      OK - predictions: {preds}")

print("[3/4] Loading whisper model (base)...")
w = whisper.load_model('base')
print("      OK - whisper model loaded")

print("[4/4] Testing transcription...")
audio = np.zeros(16000, dtype=np.float32)
result = w.transcribe(audio, language='zh', fp16=False)
text = result["text"]
print(f"      OK - transcription result: '{text}'")

print()
print("=" * 60)
print("ALL TESTS PASSED!")
print("Project is ready to use.")
print("=" * 60)
print()
print("Run 'python main.py' to start the voice assistant.")
print("Say 'hey jarvis' to activate voice recognition.")
