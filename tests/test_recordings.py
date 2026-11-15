"""Sanity checks against real singers.

Put .wav/.flac/.ogg/.mp3 clips of sustained sung notes in tests/recordings/
(see tests/recordings/README.md). Each clip is checked against the ranges
reported for trained operatic voices. If the folder is empty these tests skip.
"""
import glob
import os

import pytest

from opera_technique.analysis.pitch import extract_f0, analyze_vibrato
from opera_technique.analysis.quality import calculate_hnr
from opera_technique.analysis.resonance import calculate_ltas, find_singers_formant
from opera_technique.utils.audio import load_audio, normalize_audio, trim_silence

HERE = os.path.dirname(__file__)
CLIPS = sorted(
    p for ext in ("wav", "flac", "ogg", "mp3")
    for p in glob.glob(os.path.join(HERE, "recordings", f"*.{ext}")))

pytestmark = pytest.mark.skipif(not CLIPS, reason="no clips in tests/recordings/")


@pytest.fixture(scope="module", params=CLIPS or [None],
                ids=lambda p: os.path.basename(p) if p else "none")
def clip(request):
    y, sr = load_audio(request.param)
    return request.param, trim_silence(normalize_audio(y)), sr


def test_vibrato_in_operatic_range(clip):
    _, y, sr = clip
    f0, _, _ = extract_f0(y, sr)
    result = analyze_vibrato(f0, sr / 512)
    assert 4.0 <= result["vibrato_rate_hz"] <= 8.0
    assert 20 <= result["vibrato_extent_cents"] <= 250


def test_singers_formant_in_expected_band(clip):
    _, y, sr = clip
    freqs, psd_db = calculate_ltas(y, sr)
    assert 2500 <= find_singers_formant(freqs, psd_db)["peak_freq_hz"] <= 3500


def test_voice_is_mostly_harmonic(clip):
    path, _, _ = clip
    assert calculate_hnr(path)["mean_hnr_db"] > 5  # loose: old recordings are noisy
