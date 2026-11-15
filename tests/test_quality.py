import soundfile as sf

from opera_technique.analysis.quality import calculate_hnr, calculate_glottal_parameters
from synth import sung_note


def write(tmp_path, name, **kwargs):
    y, sr = sung_note(f0=220.0, rate_hz=5.5, extent_cents=40, **kwargs)
    path = tmp_path / name
    sf.write(path, y, sr)
    return str(path)


def test_clean_tone_has_high_hnr(tmp_path):
    result = calculate_hnr(write(tmp_path, "clean.wav"))
    assert result["mean_hnr_db"] > 20  # the "trained singer" threshold in quality.py


def test_hnr_drops_as_breathiness_increases(tmp_path):
    clean = calculate_hnr(write(tmp_path, "clean.wav"))["mean_hnr_db"]
    mild = calculate_hnr(write(tmp_path, "mild.wav", noise_level=0.1))["mean_hnr_db"]
    breathy = calculate_hnr(write(tmp_path, "breathy.wav", noise_level=0.5))["mean_hnr_db"]
    assert clean > mild > breathy


def test_glottal_parameters_are_small_for_a_stable_tone(tmp_path):
    result = calculate_glottal_parameters(write(tmp_path, "clean.wav"))
    assert 0 <= result["jitter_local"] < 0.01   # < 1 %
    assert 0 <= result["shimmer_local"] < 0.05  # < 5 %


def test_missing_file_is_handled(tmp_path):
    assert calculate_hnr(str(tmp_path / "nope.wav")) is None
    assert calculate_glottal_parameters(str(tmp_path / "nope.wav")) is None
