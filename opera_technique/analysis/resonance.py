import numpy as np
import scipy.fftpack
from scipy.signal import welch

def calculate_ltas(y, sr, nperseg=4096):
    """
    Calculates the Long-Term Average Spectrum (LTAS) using Welch's method.
    
    LTAS is a standard tool in voice research for analyzing the 
    spectral characteristics of a long speech or singing sample.

    Args:
        y (np.ndarray): Audio signal.
        sr (int): Sample rate.
        nperseg (int): Length of each segment for FFT.

    Returns:
        tuple: (frequencies, power_spectral_density_db)
    """
    freqs, psd = welch(y, sr, nperseg=nperseg)
    
    # Convert to decibels relative to max power
    psd_db = 10 * np.log10(psd / np.max(psd) + 1e-10) # Add epsilon to avoid log(0)
    
    return freqs, psd_db

def find_singers_formant(freqs, psd_db, range_min=2500, range_max=3500):
    """
    Identifies the 'Singer's Formant' peak within the 2.5kHz - 3.5kHz range.
    
    The Singer's Formant (or 'Ring') is a boost in acoustic energy that 
    allows operatic voices to project over an orchestra.

    Args:
        freqs (np.ndarray): Frequency bins from LTAS.
        psd_db (np.ndarray): Power spectral density in dB.
        range_min (int): Start of search range (Hz).
        range_max (int): End of search range (Hz).

    Returns:
        dict: {
            'peak_freq_hz': float,
            'peak_magnitude_db': float,
            'spectral_tilt_ratio': float
        }
    """
    # Filter frequencies to the specified range
    mask = (freqs >= range_min) & (freqs <= range_max)
    range_freqs = freqs[mask]
    range_psd = psd_db[mask]
    
    if len(range_psd) == 0:
        return None

    # Find the peak frequency and magnitude in the band
    peak_idx = np.argmax(range_psd)
    peak_freq = range_freqs[peak_idx]
    peak_mag = range_psd[peak_idx]
    
    # Calculate energy ratio: band energy vs low-frequency energy (<1kHz)
    # This gives an indication of how "bright" or "ringing" the voice is.
    low_freq_mask = (freqs < 1000)
    low_freq_energy = np.mean(psd_db[low_freq_mask])
    
    return {
        'peak_freq_hz': float(peak_freq),
        'peak_magnitude_db': float(peak_mag),
        'energy_ratio_db': float(peak_mag - low_freq_energy)
    }

def get_spectral_balance(freqs, psd_db):
    """
    Measures the balance between low and high frequency energy.
    
    High spectral balance often correlates with better resonance 
    and vocal efficiency.
    """
    low_band = psd_db[(freqs > 0) & (freqs < 2000)]
    high_band = psd_db[(freqs >= 2000) & (freqs < 5000)]
    
    if len(low_band) == 0 or len(high_band) == 0:
        return 0.0
        
    return np.mean(high_band) - np.mean(low_band)