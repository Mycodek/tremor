import numpy as np


def estimate_phase(signal):
    derivative = np.gradient(signal)
    return np.arctan2(derivative, signal)


def generate_correction(tremor_component, gain=1.0):
    return -gain * tremor_component


def stability_score(raw_signal, corrected_signal):
    rms_raw = np.sqrt(np.mean(raw_signal ** 2))
    rms_corrected = np.sqrt(np.mean(corrected_signal ** 2))
    if rms_raw == 0:
        return 0.0
    return max(0.0, 1.0 - rms_corrected / rms_raw)
