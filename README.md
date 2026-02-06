# Opera Technique Analysis Tool

A Python-based vocal analysis tool for measuring operatic technique, designed for both post-performance analysis and real-time feedback.

## Features
- **Pitch & Vibrato**: f0 extraction using pYIN, vibrato rate (Hz) and extent (cents).
- **Resonance**: LTAS to identify the Singer's Formant (2.5kHz - 3.5kHz).
- **Voice Quality**: Harmonic-to-Noise Ratio (HNR) for vocal fold efficiency using Praat.
- **Live Analysis**: Automatic phrase detection and reporting.
- **Visual Feedback**: Real-time FFT and Waveform visualization.

## Quick Start
1. Ensure you have Python 3.10+ installed.
2. Run the launcher:
   ```bash
   ./run.sh
   ```

## Structure
- `opera_technique/analysis/`: Core DSP logic (Pitch, Resonance, Quality).
- `opera_technique/utils/`: Audio preprocessing and helper functions.
- `opera_technique/live_session.py`: CLI-based live phrase monitor.
- `opera_technique/visual_session.py`: Real-time spectrum visualization.
- `tests/`: Unit tests (to be implemented).
- `data/`: Sample audio files.