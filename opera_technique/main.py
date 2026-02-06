import argparse
import os
import sys
import numpy as np

# Add the current directory to path so we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opera_technique.utils.audio import load_audio, normalize_audio, trim_silence
from opera_technique.analysis.pitch import extract_f0, analyze_vibrato
from opera_technique.analysis.resonance import calculate_ltas, find_singers_formant, get_spectral_balance
from opera_technique.analysis.quality import calculate_hnr, calculate_glottal_parameters

def run_analysis(input_data, sr=None):
    """
    Runs analysis on either a file path or a raw audio array.
    """
    file_path = None
    delete_temp = False

    if isinstance(input_data, str):
        print(f"\n--- Analyzing: {os.path.basename(input_data)} ---")
        y, sr = load_audio(input_data)
        file_path = input_data
    else:
        print(f"\n--- Analyzing Live Recording ---")
        y = input_data
        # Create temp file for Parselmouth (Praat)
        import soundfile as sf
        import tempfile
        tf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(tf.name, y, sr)
        tf.close()
        file_path = tf.name
        delete_temp = True

    if y is None:
        return
    
    y = normalize_audio(y)
    y = trim_silence(y)
    
    # 2. Pitch & Vibrato
    # We use a hop_length to determine the time resolution of f0
    hop_length = 512
    f0, voiced_flag, times = extract_f0(y, sr)
    sr_f0 = sr / hop_length
    
    vibrato_results = analyze_vibrato(f0, sr_f0)
    
    # 3. Resonance (LTAS)
    freqs, psd_db = calculate_ltas(y, sr)
    resonance_results = find_singers_formant(freqs, psd_db)
    balance = get_spectral_balance(freqs, psd_db)
    
    # 4. Voice Quality (HNR & Glottal)
    hnr_results = calculate_hnr(file_path)
    glottal_results = calculate_glottal_parameters(file_path)
    
    # --- Report Generation ---
    print("\n[PITCH & VIBRATO]")
    if vibrato_results:
        print(f"  Mean f0:         {vibrato_results['mean_f0_hz']:.2f} Hz")
        print(f"  Vibrato Rate:    {vibrato_results['vibrato_rate_hz']:.2f} Hz")
        print(f"  Vibrato Extent:  {vibrato_results['vibrato_extent_cents']:.2f} cents")
    
    print("\n[RESONANCE & RING]")
    if resonance_results:
        print(f"  Singer's Formant Peak: {resonance_results['peak_freq_hz']:.2f} Hz")
        print(f"  Formant Magnitude:     {resonance_results['peak_magnitude_db']:.2f} dB")
        print(f"  Energy Ratio (Ring):   {resonance_results['energy_ratio_db']:.2f} dB")
    print(f"  Spectral Balance:      {balance:.2f} dB (High-Low ratio)")
    
    print("\n[VOICE QUALITY]")
    if hnr_results:
        print(f"  Mean HNR:        {hnr_results['mean_hnr_db']:.2f} dB")
    if glottal_results:
        print(f"  Jitter (local):  {glottal_results['jitter_local']*100:.3f}%")
        print(f"  Shimmer (local): {glottal_results['shimmer_local']*100:.3f}%")
    
    print("\n--- Analysis Complete ---\n")

    # Cleanup temp file if created
    if delete_temp and os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Operatic Technique Analysis Tool")
    parser.add_argument("file", help="Path to the audio file (.wav)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
    else:
        run_analysis(args.file)