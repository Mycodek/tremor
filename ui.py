import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from signal_generator import (
    generate_signal, FINGER_NAMES, FINGER_DEFAULTS,
    MEDICAL_PRESETS, PRESET_NAMES,
)
from tremor_detector import bandpass_filter, estimate_frequency
from correction import generate_correction, stability_score

FINGER_COLORS = {
    "Thumb": "#e74c3c",
    "Index": "#3498db",
    "Middle": "#2ecc71",
    "Ring": "#f39c12",
    "Pinky": "#9b59b6",
}


def _apply_preset():
    """Callback: push preset values into session_state so sliders pick them up."""
    name = st.session_state.preset_select
    if name == "Custom":
        return
    preset = MEDICAL_PRESETS[name]
    for key, val in preset["globals"].items():
        st.session_state[key] = val
    for finger, cfg in preset["fingers"].items():
        st.session_state[f"{finger}_freq"] = cfg["tremor_freq"]
        st.session_state[f"{finger}_amp"] = cfg["tremor_amp"]


def run():
    st.set_page_config(page_title="Tremor Stabilization Simulator", layout="wide")

    title_col, info_col = st.columns([8, 1])
    title_col.title("Tremor Stabilization Simulator")
    with info_col.popover("ℹ️", use_container_width=True):
        st.markdown("""
**Dashboard Guide**

---

**Raw Signal** *(gray line)*
Simulated finger motion = voluntary movement + tremor + sensor noise.
Unit: relative amplitude (dimensionless). In a real device this maps to
angular displacement (degrees) or acceleration (m/s²) from an IMU.

**Detected Tremor** *(colored line)*
The tremor component isolated by a Butterworth band-pass filter.
Only oscillations within the configured frequency band are kept;
slow voluntary motion and high-frequency noise are rejected.

**Corrected Signal** *(dashed line)*
Result after subtracting `gain × detected_tremor` from the raw signal.
At gain = 1.0 the tremor is fully cancelled. Gain > 1 over-corrects and
re-injects inverted tremor energy.

---

**Stability Score** *(per finger, %)*
`1 − RMS(corrected) / RMS(raw)` expressed as a percentage.
Higher = more energy removed. ~25-40 % is a realistic good outcome;
100 % would mean all motion (including voluntary) was eliminated.

**Estimated Frequency** *(per finger, Hz)*
Dominant oscillation frequency inside the detected tremor band,
found via FFT peak detection. Typical clinical ranges:
- Essential tremor: 4–12 Hz
- Parkinsonian resting tremor: 4–6 Hz

**Overall Score**
Arithmetic mean of all five finger stability scores.

---

**Real-World Alignment**

| Parameter | Simulator | Physical glove |
|---|---|---|
| Tremor Freq | Slider (Hz) | IMU sensor → FFT |
| Tremor Amp | Slider (relative) | Accelerometer g-force |
| Filter Band | Slider (Hz) | DSP on microcontroller |
| Correction Gain | Slider (K) | Actuator drive strength |
| Stability Score | RMS ratio | Clinical tremor rating scale |

The simulator validates the *algorithm* (detect → isolate → cancel)
independently of hardware. The same pipeline runs on an ESP32 with
real IMU data when the physical glove is built.
""")

    st.caption("Multi-finger tremor detection, correction, and real-time stabilization dashboard")

    fs = 120
    duration = 5
    t = np.linspace(0, duration, fs * duration)

    # --- Medical preset selector ---
    st.sidebar.header("Medical Presets")
    preset_name = st.sidebar.selectbox(
        "Condition", PRESET_NAMES,
        key="preset_select", on_change=_apply_preset,
    )
    if preset_name != "Custom":
        st.sidebar.info(MEDICAL_PRESETS[preset_name]["description"])

    st.sidebar.divider()

    # --- Global controls (all use explicit keys for preset wiring) ---
    st.sidebar.header("Global Controls")
    voluntary_freq = st.sidebar.slider(
        "Voluntary Motion Freq (Hz)", 0.1, 3.0, 0.5, 0.1, key="voluntary_freq",
    )
    voluntary_amp = st.sidebar.slider(
        "Voluntary Motion Amp", 0.0, 3.0, 1.0, 0.1, key="voluntary_amp",
    )
    noise_amp = st.sidebar.slider(
        "Noise Amplitude", 0.0, 0.5, 0.05, 0.01, key="noise_amp",
    )

    st.sidebar.header("Filter Band")
    low_cutoff = st.sidebar.slider(
        "Low Cutoff (Hz)", 2.0, 8.0, 4.0, 0.5, key="low_cutoff",
    )
    high_cutoff = st.sidebar.slider(
        "High Cutoff (Hz)", 8.0, 15.0, 12.0, 0.5, key="high_cutoff",
    )

    st.sidebar.header("Correction")
    gain = st.sidebar.slider(
        "Correction Gain (K)", 0.0, 2.0, 1.0, 0.05, key="gain",
    )

    # --- Per-finger overrides ---
    st.sidebar.header("Per-Finger Tremor")
    finger_configs = {}
    for name in FINGER_NAMES:
        defaults = FINGER_DEFAULTS[name]
        with st.sidebar.expander(name):
            freq = st.slider(
                f"{name} Tremor Freq (Hz)", 4.0, 12.0,
                defaults["tremor_freq"], 0.1, key=f"{name}_freq",
            )
            amp = st.slider(
                f"{name} Tremor Amp", 0.0, 2.0,
                defaults["tremor_amp"], 0.05, key=f"{name}_amp",
            )
            finger_configs[name] = {"tremor_freq": freq, "tremor_amp": amp}

    # --- Compute per-finger ---
    results = {}
    for name in FINGER_NAMES:
        cfg = finger_configs[name]
        sig, trem_true, vol = generate_signal(
            t, tremor_freq=cfg["tremor_freq"], tremor_amp=cfg["tremor_amp"],
            voluntary_freq=voluntary_freq, voluntary_amp=voluntary_amp,
            noise_amp=noise_amp,
        )
        trem_est = bandpass_filter(sig, fs, low=low_cutoff, high=high_cutoff)
        freq_est = estimate_frequency(trem_est, fs)
        corr = generate_correction(trem_est, gain=gain)
        corrected = sig + corr
        score = stability_score(sig, corrected)
        results[name] = {
            "signal": sig, "tremor_est": trem_est,
            "corrected": corrected, "freq_est": freq_est, "score": score,
        }

    # --- Summary metrics ---
    st.subheader("Stability Overview")
    cols = st.columns(len(FINGER_NAMES) + 1)
    for i, name in enumerate(FINGER_NAMES):
        r = results[name]
        cols[i].metric(
            name,
            f"{r['score'] * 100:.1f}%",
            f"{r['freq_est']:.1f} Hz",
        )
    overall = np.mean([results[n]["score"] for n in FINGER_NAMES])
    cols[-1].metric("Overall", f"{overall * 100:.1f}%")

    st.divider()

    # --- Per-finger plots ---
    fig, axes = plt.subplots(len(FINGER_NAMES), 1, figsize=(14, 3 * len(FINGER_NAMES)),
                             sharex=True)
    for ax, name in zip(axes, FINGER_NAMES):
        r = results[name]
        color = FINGER_COLORS[name]
        ax.plot(t, r["signal"], linewidth=0.5, alpha=0.4, color="gray", label="Raw")
        ax.plot(t, r["tremor_est"], linewidth=0.7, alpha=0.6, color=color, label="Tremor")
        ax.plot(t, r["corrected"], linewidth=1.0, color=color, alpha=0.9,
                linestyle="--", label="Corrected")
        ax.set_ylabel(name, fontweight="bold", color=color)
        ax.legend(loc="upper right", fontsize=7)
        ax.grid(True, alpha=0.2)

    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("Per-Finger Tremor Detection & Correction", fontsize=14, y=1.01)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
