import whisper
import time
import numpy as np

print("Loading whisper base model...")
t0 = time.time()
w = whisper.load_model("base")
print(f"Loaded in {time.time()-t0:.1f} seconds")

print("Testing transcription...")
audio = np.zeros(16000, dtype=np.float32)
result = w.transcribe(audio, language="zh", fp16=False)
text = result["text"]
print(f"Transcription result: {text}")
print("SUCCESS")
