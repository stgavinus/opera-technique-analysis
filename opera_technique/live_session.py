import sounddevice as sd
import numpy as np
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from opera_technique.main import run_analysis

# Config
SR = 44100
BLOCK_SIZE = 1024
CHANNELS = 1
SILENCE_THRESHOLD = 0.01  # Adjust based on mic sensitivity
SILENCE_DURATION = 1.0    # Seconds of silence to trigger end of phrase
MAX_PHRASE_LEN = 10       # Max seconds to record
MIN_PHRASE_LEN = 0.5      # Min seconds to consider valid

def live_session():
    print(f"Initializing Audio Stream (SR={SR}, Channels={CHANNELS})...")
    print("---------------------------------------------------------")
    print(" INSTRUCTIONS:")
    print(" 1. Sing a phrase clearly.")
    print(" 2. Pause for a second.")
    print(" 3. Results will appear instantly.")
    print(" 4. Repeat.")
    print(" Press Ctrl+C to exit.")
    print("---------------------------------------------------------")

    try:
        # Determine device (optional, defaults to system default)
        device_info = sd.query_devices(kind='input')
        print(f"Using Input Device: {device_info['name']}")

        buffer = []
        is_recording = False
        silence_start = None
        
        def callback(indata, frames, time_info, status):
            nonlocal buffer, is_recording, silence_start
            if status:
                print(status, file=sys.stderr)
            
            # Compute RMS amplitude
            amplitude = np.sqrt(np.mean(indata**2))
            
            if is_recording:
                buffer.append(indata.copy())
                
                # Check for silence
                if amplitude < SILENCE_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > SILENCE_DURATION:
                        # End of phrase detected
                        is_recording = False
                        process_buffer(buffer)
                        buffer = [] # Reset
                        silence_start = None
                        print("\nListening...")
                else:
                    silence_start = None # Reset silence timer if sound returns
                
                # Safety valve: Max length
                if len(buffer) * BLOCK_SIZE / SR > MAX_PHRASE_LEN:
                    is_recording = False
                    process_buffer(buffer)
                    buffer = []
                    silence_start = None
                    print("\nListening...")

            else:
                # Trigger recording start
                if amplitude > SILENCE_THRESHOLD:
                    print("\n[Recording...]")
                    is_recording = True
                    buffer.append(indata.copy())
                    silence_start = None

        def process_buffer(buf):
            # Concatenate blocks
            audio_data = np.concatenate(buf, axis=0).flatten()
            
            duration = len(audio_data) / SR
            if duration < MIN_PHRASE_LEN:
                print("(Phrase too short, ignoring)")
                return

            # Run analysis
            try:
                run_analysis(audio_data, sr=SR)
            except Exception as e:
                print(f"Analysis Failed: {e}")

        # Start stream
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SR, blocksize=BLOCK_SIZE):
            while True:
                sd.sleep(100)

    except KeyboardInterrupt:
        print("\nSession ended.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Tip: Ensure you have a working microphone and 'sounddevice' installed.")

if __name__ == "__main__":
    live_session()