import librosa
import numpy as np
from scipy.signal import find_peaks

def extract_f0(y, sr, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C6')):
    """
    Extracts the fundamental frequency (f0) using the pYIN algorithm.
    
    pYIN is preferred for operatic vocals as it handles vibrato and 
    transitions more robustly than basic autocorrelation methods.

    Args:
        y (np.ndarray): Audio signal.
        sr (int): Sample rate.
        fmin (float): Minimum frequency to detect.
        fmax (float): Maximum frequency to detect.

    Returns:
        tuple: (f0, voiced_flag, times)
    """
    # pYIN returns f0, voiced_flag (boolean), and voiced_probabilities
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr)
    
    # Calculate timestamps for each frame
    times = librosa.times_like(f0, sr=sr)
    
    return f0, voiced_flag, times

def hz_to_cents(frequencies, reference_hz):
    """
    Converts a frequency array from Hz to cents relative to a reference.
    
    Formula: cents = 1200 * log2(f / f_ref)
    """
    # Filter out NaNs and zeros to avoid log errors
    valid_mask = (frequencies > 0) & (~np.isnan(frequencies))
    cents = np.zeros_like(frequencies)
    cents[valid_mask] = 1200 * np.log2(frequencies[valid_mask] / reference_hz)
    return cents

def analyze_vibrato(f0, sr_f0):
    """
    Calculates vibrato rate and extent from the f0 curve.
    
    Operatic vibrato typically sits between 5-7 Hz with an extent of 
    +/- 50 to 150 cents.

    Args:
        f0 (np.ndarray): The extracted f0 curve (Hz).
        sr_f0 (float): The sample rate of the f0 analysis (usually sr/hop_length).

    Returns:
        dict: {
            'vibrato_rate_hz': float,
            'vibrato_extent_cents': float,
            'mean_f0_hz': float
        }
    """
    # Remove NaNs for analysis
    valid_f0 = f0[~np.isnan(f0)]
    if len(valid_f0) < 2:
        return None

    mean_f0 = np.mean(valid_f0)
    
    # Convert f0 to cents relative to its own mean to isolate oscillation
    f0_cents = hz_to_cents(valid_f0, mean_f0)
    
    # Detrend the signal (remove DC offset)
    f0_detrended = f0_cents - np.mean(f0_cents)

    # Find peaks in the pitch curve to estimate rate
    # We expect 5-7 oscillations per second.
    # distance = sr_f0 / max_expected_rate
    peaks, _ = find_peaks(f0_detrended, distance=sr_f0/10)
    
    if len(peaks) < 2:
        return {
            'vibrato_rate_hz': 0.0,
            'vibrato_extent_cents': 0.0,
            'mean_f0_hz': mean_f0
        }

    # Calculate rate: Mean distance between peaks converted to Hz
    peak_diffs = np.diff(peaks)
    avg_peak_dist = np.mean(peak_diffs)
    rate_hz = sr_f0 / avg_peak_dist
    
    # Calculate extent: Root Mean Square of the cents curve * sqrt(2) 
    # to estimate peak amplitude, or use mean peak height.
    extent_cents = np.mean(np.abs(f0_detrended[peaks]))
    
    return {
        'vibrato_rate_hz': rate_hz,
        'vibrato_extent_cents': extent_cents,
        'mean_f0_hz': mean_f0
    }