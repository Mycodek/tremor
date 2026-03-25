import numpy as np

FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

FINGER_DEFAULTS = {
    "Thumb":  {"tremor_freq": 6.0, "tremor_amp": 0.30},
    "Index":  {"tremor_freq": 7.0, "tremor_amp": 0.45},
    "Middle": {"tremor_freq": 7.5, "tremor_amp": 0.40},
    "Ring":   {"tremor_freq": 8.0, "tremor_amp": 0.35},
    "Pinky":  {"tremor_freq": 8.5, "tremor_amp": 0.25},
}

# Clinically informed presets.
# Essential tremor: action/postural, 4-12 Hz, amplitude rises and frequency
# drifts lower as the condition progresses across stages.
# Parkinson's: resting tremor, 4-6 Hz, asymmetric, pill-rolling pattern.
MEDICAL_PRESETS = {
    "ET Stage 1 -- Mild": {
        "description": (
            "Early essential tremor. Barely visible, mainly index and middle "
            "fingers during sustained posture. High frequency, low amplitude."
        ),
        "globals": {
            "voluntary_freq": 0.5, "voluntary_amp": 1.0, "noise_amp": 0.03,
            "low_cutoff": 5.0, "high_cutoff": 12.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 9.0,  "tremor_amp": 0.10},
            "Index":  {"tremor_freq": 9.5,  "tremor_amp": 0.15},
            "Middle": {"tremor_freq": 9.0,  "tremor_amp": 0.12},
            "Ring":   {"tremor_freq": 8.5,  "tremor_amp": 0.08},
            "Pinky":  {"tremor_freq": 8.0,  "tremor_amp": 0.05},
        },
    },
    "ET Stage 2 -- Moderate": {
        "description": (
            "Noticeable essential tremor. Affects writing and pouring. "
            "All fingers involved, index and middle dominant."
        ),
        "globals": {
            "voluntary_freq": 0.5, "voluntary_amp": 1.0, "noise_amp": 0.04,
            "low_cutoff": 4.5, "high_cutoff": 12.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 8.0,  "tremor_amp": 0.25},
            "Index":  {"tremor_freq": 8.5,  "tremor_amp": 0.35},
            "Middle": {"tremor_freq": 8.0,  "tremor_amp": 0.30},
            "Ring":   {"tremor_freq": 7.5,  "tremor_amp": 0.20},
            "Pinky":  {"tremor_freq": 7.0,  "tremor_amp": 0.15},
        },
    },
    "ET Stage 3 -- Pronounced": {
        "description": (
            "Pronounced essential tremor. Interferes with eating and "
            "dressing. Frequency drifts lower, amplitude clearly visible."
        ),
        "globals": {
            "voluntary_freq": 0.5, "voluntary_amp": 1.0, "noise_amp": 0.05,
            "low_cutoff": 4.0, "high_cutoff": 11.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 7.0,  "tremor_amp": 0.45},
            "Index":  {"tremor_freq": 7.5,  "tremor_amp": 0.55},
            "Middle": {"tremor_freq": 7.0,  "tremor_amp": 0.50},
            "Ring":   {"tremor_freq": 6.5,  "tremor_amp": 0.40},
            "Pinky":  {"tremor_freq": 6.0,  "tremor_amp": 0.30},
        },
    },
    "ET Stage 4 -- Severe": {
        "description": (
            "Severe essential tremor. Fine motor tasks nearly impossible "
            "without assistance. Large-amplitude, lower-frequency oscillation."
        ),
        "globals": {
            "voluntary_freq": 0.5, "voluntary_amp": 1.0, "noise_amp": 0.06,
            "low_cutoff": 3.5, "high_cutoff": 10.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 6.0,  "tremor_amp": 0.70},
            "Index":  {"tremor_freq": 6.5,  "tremor_amp": 0.85},
            "Middle": {"tremor_freq": 6.0,  "tremor_amp": 0.80},
            "Ring":   {"tremor_freq": 5.5,  "tremor_amp": 0.65},
            "Pinky":  {"tremor_freq": 5.0,  "tremor_amp": 0.50},
        },
    },
    "ET Stage 5 -- Debilitating": {
        "description": (
            "End-stage essential tremor. Cannot hold objects or feed "
            "independently. Very high amplitude across all fingers."
        ),
        "globals": {
            "voluntary_freq": 0.4, "voluntary_amp": 0.8, "noise_amp": 0.08,
            "low_cutoff": 3.0, "high_cutoff": 9.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 5.0,  "tremor_amp": 1.00},
            "Index":  {"tremor_freq": 5.5,  "tremor_amp": 1.20},
            "Middle": {"tremor_freq": 5.0,  "tremor_amp": 1.10},
            "Ring":   {"tremor_freq": 4.5,  "tremor_amp": 0.90},
            "Pinky":  {"tremor_freq": 4.5,  "tremor_amp": 0.75},
        },
    },
    "Parkinson's Disease -- Resting Tremor": {
        "description": (
            "Classic Parkinsonian resting tremor at 4-6 Hz. Asymmetric "
            "presentation with thumb and index most affected (pill-rolling). "
            "Tremor suppresses during voluntary movement."
        ),
        "globals": {
            "voluntary_freq": 0.3, "voluntary_amp": 0.6, "noise_amp": 0.04,
            "low_cutoff": 3.0, "high_cutoff": 8.0, "gain": 1.0,
        },
        "fingers": {
            "Thumb":  {"tremor_freq": 5.0,  "tremor_amp": 0.80},
            "Index":  {"tremor_freq": 5.0,  "tremor_amp": 0.75},
            "Middle": {"tremor_freq": 4.5,  "tremor_amp": 0.50},
            "Ring":   {"tremor_freq": 4.5,  "tremor_amp": 0.40},
            "Pinky":  {"tremor_freq": 4.0,  "tremor_amp": 0.30},
        },
    },
}

PRESET_NAMES = ["Custom"] + list(MEDICAL_PRESETS.keys())


def generate_signal(t, tremor_freq=7.0, tremor_amp=0.4,
                    voluntary_freq=0.5, voluntary_amp=1.0,
                    noise_amp=0.05):
    tremor = tremor_amp * np.sin(2 * np.pi * tremor_freq * t)
    voluntary = voluntary_amp * np.sin(2 * np.pi * voluntary_freq * t)
    noise = noise_amp * np.random.randn(len(t))
    return voluntary + tremor + noise, tremor, voluntary
