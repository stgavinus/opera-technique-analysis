import parselmouth
import numpy as np

def calculate_hnr(file_path, time_step=0.01, f0_min=75, silence_threshold=0.1):
    """
    Calculates the Harmonic-to-Noise Ratio (HNR) using Praat's algorithm via Parselmouth.
    
    HNR measures the ratio between periodic (harmonic) and aperiodic (noise) 
    components of the voice. Higher values (typically > 20dB for trained singers) 
    indicate cleaner vocal fold closure and less breathiness.

    Args:
        file_path (str): Path to the audio file (Praat works best with file paths).
        time_step (float): Time step in seconds for analysis.
        f0_min (float): Minimum frequency to consider for pitch analysis.
        silence_threshold (float): Threshold for silence detection.

    Returns:
        dict: {
            'mean_hnr_db': float,
            'max_hnr_db': float,
            'hnr_values': np.ndarray
        }
    """
    try:
        # Load sound into Parselmouth
        sound = parselmouth.Sound(file_path)
        
        # Calculate HNR (Harmonicity) using the cross-correlation method (standard in Praat)
        harmonicity = sound.to_harmonicity(
            time_step=time_step, 
            minimum_pitch=f0_min, 
            silence_threshold=silence_threshold
        )
        
        # Extract values
        hnr_values = harmonicity.values[harmonicity.values != -200] # -200 is Praat's 'undefined' value
        
        if len(hnr_values) == 0:
            return None

        return {
            'mean_hnr_db': float(np.mean(hnr_values)),
            'max_hnr_db': float(np.max(hnr_values)),
            'hnr_values': hnr_values
        }
    except Exception as e:
        print(f"Error calculating HNR: {e}")
        return None

def calculate_glottal_parameters(file_path):
    """
    Placeholder for more advanced glottal flow analysis.
    In a full implementation, this could include Jitter and Shimmer
    which measure frequency and amplitude perturbations.
    """
    try:
        sound = parselmouth.Sound(file_path)
        point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 600)
        
        local_jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        local_shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        
        return {
            'jitter_local': float(local_jitter),
            'shimmer_local': float(local_shimmer)
        }
    except Exception:
        return None