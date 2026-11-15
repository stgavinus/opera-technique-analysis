import numpy as np
import pytest

from opera_technique.analysis.pitch import extract_f0, analyze_vibrato, hz_to_cents
from synth import sung_note

HOP = 512  # librosa.pyin default hop length (frame_length 2048 // 4)


def run(y, sr):
    f0, voiced, _ = extract_f0(y, sr)
    return f0, voiced, analyze_vibrato(f0, sr / HOP)


def test_hz_to_cents_known_intervals():
    cents = hz_to_cents(np.array([440.0, 880.0, 220.0, 466.1638]), 440.0)
    assert cents == pytest.approx([0, 1200, -1200, 100], abs=0.01)


def test_hz_to_cents_ignores_unvoiced_frames():
    cents = hz_to_cents(np.array([np.nan, 0.0, 440.0]), 440.0)
    assert cents.tolist() == [0.0, 0.0, 0.0]


@pytest.mark.parametrize("f0", [196.0, 293.66, 440.0, 659.25])  # G3, D4, A4, E5
def test_steady_pitch_is_detected(f0):
    y, sr = sung_note(f0=f0, extent_cents=0, duration=2.0)
    f0_track, voiced, _ = run(y, sr)
    assert voiced.mean() > 0.9
    assert np.nanmedian(f0_track) == pytest.approx(f0, rel=0.01)  # within ~17 cents


@pytest.mark.parametrize("rate", [5.0, 5.5, 6.5])
def test_vibrato_rate(rate):
    y, sr = sung_note(f0=440.0, rate_hz=rate, extent_cents=80)
    _, _, result = run(y, sr)
    assert result["vibrato_rate_hz"] == pytest.approx(rate, abs=0.3)


@pytest.mark.parametrize("extent", [50.0, 100.0])
def test_vibrato_extent(extent):
    y, sr = sung_note(f0=440.0, rate_hz=5.5, extent_cents=extent)
    _, _, result = run(y, sr)
    assert result["vibrato_extent_cents"] == pytest.approx(extent, rel=0.2)


def test_mean_pitch_survives_vibrato():
    y, sr = sung_note(f0=392.0, rate_hz=5.5, extent_cents=100)
    _, _, result = run(y, sr)
    assert result["mean_f0_hz"] == pytest.approx(392.0, rel=0.01)


def test_straight_tone_reports_negligible_extent():
    y, sr = sung_note(f0=440.0, extent_cents=0)
    _, _, result = run(y, sr)
    assert result["vibrato_extent_cents"] < 10


def test_silence_returns_none():
    sr = 44100
    _, _, result = run(np.zeros(sr, dtype=np.float32), sr)
    assert result is None
