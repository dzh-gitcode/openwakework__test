import sounddevice as sd
import numpy as np

print("Testing audio input...")

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Status: {status}")
    print(f"Received {len(indata)} samples")

try:
    devices = sd.query_devices()
    print("\nAvailable audio devices:")
    for i, dev in enumerate(devices):
        print(f"{i}: {dev['name']}")
    
    default_device = sd.default.device[0]
    print(f"\nUsing default input device: {devices[default_device]['name']}")
    
    print("\nTesting audio stream... (press Ctrl+C to stop)")
    with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback, blocksize=1280):
        while True:
            pass
            
except KeyboardInterrupt:
    print("\nTest completed!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()