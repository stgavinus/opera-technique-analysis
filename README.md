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

To analyze a recording instead of live input:

```bash
./venv/bin/python opera_technique/main.py path/to/recording.wav
```

## Testing

```bash
./venv/bin/pip install pytest
./venv/bin/python -m pytest tests
```

The suite checks each measurement against signals whose true values are known. `tests/synth.py` generates a harmonic tone with a sinusoidal vibrato of a chosen rate and extent, an optional formant boost near 3 kHz, and optional breath noise. The tests confirm that:

- steady pitches from G3 to E5 are detected within 1%,
- vibrato rates of 5 to 6.5 Hz are measured within 0.3 Hz, and extent within 20%,
- a 3 kHz formant boost is located within 150 Hz and raises the ring and spectral-balance scores,
- HNR is above 20 dB for a clean tone and falls steadily as noise is added.

`tests/test_recordings.py` also runs every clip in `tests/recordings/` against the ranges reported for trained operatic voices (see that folder's README).

## Structure
- `opera_technique/analysis/`: Core DSP logic (pitch, resonance, quality).
- `opera_technique/utils/`: Audio loading and preprocessing.
- `opera_technique/main.py`: Analyze an audio file and print a report.
- `opera_technique/live_session.py`: CLI-based live phrase monitor.
- `opera_technique/visual_session.py`: Real-time spectrum visualization.
- `tests/`: Unit tests on synthetic signals, plus optional checks on real recordings.