import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(signal, fs, low=4, high=12, order=4):
    nyquist = 0.5 * fs
    b, a = butter(order, [low / nyquist, high / nyquist], btype="band")
    return filtfilt(b, a, signal)


def estimate_frequency(signal, fs):
    fft_vals = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1 / fs)
    return freqs[np.argmax(np.abs(fft_vals))]
