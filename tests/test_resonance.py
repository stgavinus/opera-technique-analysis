import pytest

from opera_technique.analysis.resonance import (
    calculate_ltas, find_singers_formant, get_spectral_balance)
from synth import sung_note


def analyze(**kwargs):
    y, sr = sung_note(f0=220.0, extent_cents=0, n_harmonics=40, **kwargs)
    freqs, psd_db = calculate_ltas(y, sr)
    return find_singers_formant(freqs, psd_db), get_spectral_balance(freqs, psd_db)


def test_ltas_is_normalised_to_0_db_peak():
    y, sr = sung_note(f0=220.0, extent_cents=0)
    _, psd_db = calculate_ltas(y, sr)
    assert psd_db.max() == pytest.approx(0.0, abs=1e-6)


def test_singers_formant_peak_is_located():
    ring, _ = analyze(formant_hz=3000, formant_gain_db=24)
    assert ring["peak_freq_hz"] == pytest.approx(3000, abs=150)


def test_formant_boost_raises_ring_and_balance():
    plain_ring, plain_balance = analyze()
    ringing, ringing_balance = analyze(formant_hz=3000, formant_gain_db=24)
    assert ringing["energy_ratio_db"] > plain_ring["energy_ratio_db"] + 10
    assert ringing_balance > plain_balance


def test_search_band_outside_spectrum_returns_none():
    y, sr = sung_note(f0=220.0, extent_cents=0)
    freqs, psd_db = calculate_ltas(y, sr)
    assert find_singers_formant(freqs, psd_db, 30000, 40000) is None
