import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sounddevice as sd
import queue
import sys

# Audio Config
SR = 44100
BLOCK_SIZE = 2048  # Larger block size for better freq resolution
CHANNELS = 1
DOWNSAMPLE = 1    # Display every Nth sample for waveform speed

# Queue to transfer data between audio callback and main thread
q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def visual_session():
    print("Initializing Visual Session...")
    print("Close the window to stop.")

    # Setup Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle('Real-Time Operatic Analysis')

    # 1. Waveform Plot
    x = np.arange(0, BLOCK_SIZE, DOWNSAMPLE)
    line_wave, = ax1.plot(x, np.zeros(len(x)), '-', lw=1)
    ax1.set_title('Waveform')
    ax1.set_ylim(-0.5, 0.5)
    ax1.set_xlim(0, BLOCK_SIZE)
    ax1.grid(True, alpha=0.3)

    # 2. Spectrum Plot (FFT)
    freqs = np.fft.rfftfreq(BLOCK_SIZE, 1/SR)
    line_fft, = ax2.plot(freqs, np.zeros(len(freqs)), '-', lw=1, color='orange')
    
    # Highlight Singer's Formant Region (2.5k - 3.5k)
    ax2.axvspan(2500, 3500, color='red', alpha=0.2, label="Singer's Formant")
    ax2.legend()
    
    ax2.set_title('Spectrum (Look for energy in the red band!)')
    ax2.set_xlim(0, 5000)  # Focus on 0-5kHz (Voice range)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel('Frequency (Hz)')
    ax2.grid(True, alpha=0.3)

    # Stream object
    stream = sd.InputStream(
        callback=audio_callback,
        channels=CHANNELS,
        samplerate=SR,
        blocksize=BLOCK_SIZE
    )

    def update(frame):
        while True:
            try:
                data = q.get_nowait()
            except queue.Empty:
                break
            
            # Update Waveform
            shift = len(data)
            line_wave.set_ydata(data[:, 0])
            
            # Update FFT
            # Windowing (Hanning) to reduce leakage
            windowed = data[:, 0] * np.hanning(len(data))
            fft_data = np.abs(np.fft.rfft(windowed))
            
            # Normalize FFT for display
            fft_norm = fft_data / (len(data) / 2) # Basic normalization
            
            # Log scale for better visibility of formants (optional, strictly linear here for simplicity)
            # visual boost
            line_fft.set_ydata(fft_norm * 5) 

        return line_wave, line_fft

    ani = FuncAnimation(fig, update, interval=30, blit=True, cache_frame_data=False)

    with stream:
        plt.show()

if __name__ == "__main__":
    try:
        visual_session()
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as e:
        print(f"Error: {e}")
