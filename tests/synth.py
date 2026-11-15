"""Synthetic test signals with known ground truth.

A sung note is modelled as a harmonic series whose fundamental is frequency-
modulated by a sinusoidal vibrato:

    f(t) = f0 * 2 ** ((extent_cents / 1200) * sin(2*pi*rate*t))

so the true mean pitch, vibrato rate and vibrato extent are known exactly.
"""
import numpy as np

SR = 44100


def sung_note(f0=440.0, rate_hz=5.5, extent_cents=80.0, duration=3.0,
              n_harmonics=20, formant_hz=None, formant_gain_db=0.0,
              formant_bw_hz=400.0, noise_level=0.0, sr=SR, seed=0):
    """Return (y, sr) for a vibrato tone.

    formant_hz / formant_gain_db add a Gaussian-shaped spectral boost (e.g. a
    singer's formant near 3 kHz). noise_level adds white noise with that RMS
    relative to the tonal part's RMS.
    """
    t = np.arange(int(duration * sr)) / sr
    inst_f = f0 * 2 ** ((extent_cents / 1200.0) * np.sin(2 * np.pi * rate_hz * t))
    phase = 2 * np.pi * np.cumsum(inst_f) / sr

    y = np.zeros_like(t)
    for k in range(1, n_harmonics + 1):
        if k * f0 * 2 ** (extent_cents / 1200.0) >= sr / 2:
            break
        amp = 1.0 / k
        if formant_hz is not None and formant_gain_db:
            boost = np.exp(-0.5 * ((k * f0 - formant_hz) / formant_bw_hz) ** 2)
            amp *= 10 ** (formant_gain_db * boost / 20.0)
        y += amp * np.sin(k * phase)

    if noise_level:
        rng = np.random.default_rng(seed)
        y += noise_level * np.sqrt(np.mean(y ** 2)) * rng.standard_normal(len(y))

    return (y / np.max(np.abs(y))).astype(np.float32), sr
