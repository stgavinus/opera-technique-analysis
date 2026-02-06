import librosa
import numpy as np

def load_audio(file_path, sr=44100, mono=True):
    """
    Loads an audio file and standardizes it to a target sample rate.
    
    In operatic analysis, a high sample rate (e.g., 44.1kHz or 48kHz) is 
    essential for capturing high-frequency components like the Singer's Formant.

    Args:
        file_path (str): Path to the audio file.
        sr (int): Target sample rate. Defaults to 44100.
        mono (bool): Convert to mono if True. Defaults to True.

    Returns:
        tuple: (y, sr) where y is the audio signal and sr is the sample rate.
    """
    try:
        y, actual_sr = librosa.load(file_path, sr=sr, mono=mono)
        return y, actual_sr
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None, None

def normalize_audio(y):
    """
    Normalizes the audio signal to a peak amplitude of 1.0.
    
    Consistent amplitude levels are important for comparative LTAS 
    and HNR analysis.

    Args:
        y (np.ndarray): Audio signal.

    Returns:
        np.ndarray: Normalized audio signal.
    """
    if y is None or len(y) == 0:
        return y
    
    # Use max absolute value to avoid clipping
    max_val = np.max(np.abs(y))
    if max_val > 0:
        return y / max_val
    return y

def trim_silence(y, top_db=30):
    """
    Trims leading and trailing silence.
    
    Useful for ensuring the analysis only focuses on the sung content.

    Args:
        y (np.ndarray): Audio signal.
        top_db (int): The threshold (in decibels) below reference to consider as silence.

    Returns:
        np.ndarray: Trimmed audio signal.
    """
    yt, _ = librosa.effects.trim(y, top_db=top_db)
    return yt