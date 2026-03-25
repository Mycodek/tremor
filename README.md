# Tremor-Stabilizing Glove Simulator

A digital prototype that simulates and visualizes real-time tremor detection and cancellation across all five fingers of a hand. Built to validate the signal-processing algorithm before moving to physical hardware.

## What It Does

1. **Generates** synthetic finger motion signals (voluntary movement + tremor oscillation + sensor noise)
2. **Detects** the tremor component using a Butterworth band-pass filter (configurable 2-15 Hz)
3. **Estimates** dominant tremor frequency per finger via FFT peak detection
4. **Corrects** the signal by applying inverse cancellation with a tunable gain factor
5. **Displays** a multi-finger dashboard with per-finger and overall stability scores

## Algorithm Pipeline

```
raw motion signal  (voluntary + tremor + noise)
        |
  band-pass filter  (Butterworth, 4th order)
        |
  tremor component extraction
        |
  FFT dominant frequency estimation
        |
  phase detection   (arctan2 of derivative vs signal)
        |
  inverse correction signal  (-K * tremor_component)
        |
  corrected signal  (raw + correction)
```

## Medical Presets

The dashboard includes 6 clinically informed presets selectable from a dropdown:

| Preset | Frequency Range | Description |
|--------|----------------|-------------|
| ET Stage 1 -- Mild | 8-9.5 Hz | Barely visible, early onset |
| ET Stage 2 -- Moderate | 7-8.5 Hz | Affects writing and pouring |
| ET Stage 3 -- Pronounced | 6-7.5 Hz | Interferes with eating and dressing |
| ET Stage 4 -- Severe | 5-6.5 Hz | Fine motor tasks nearly impossible |
| ET Stage 5 -- Debilitating | 4.5-5.5 Hz | Cannot hold objects independently |
| Parkinson's Disease | 4-5 Hz | Asymmetric resting tremor, pill-rolling pattern |

Each preset configures all five fingers with realistic per-finger frequency and amplitude values derived from clinical tremor characteristics.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Signal processing | NumPy, SciPy (`butter`, `filtfilt`, `rfft`) |
| Visualization | Matplotlib |
| Dashboard | Streamlit |

## Project Structure

```
tremor/
  main.py                # entry point
  ui.py                  # Streamlit dashboard and layout
  signal_generator.py    # synthetic signal generation + medical presets
  tremor_detector.py     # band-pass filter + FFT frequency estimation
  correction.py          # phase estimation + inverse correction + stability score
  requirements.txt       # Python dependencies
  Makefile               # bootstrap, run, clean commands
```

## Quick Start

```bash
make bootstrap   # creates virtualenv and installs dependencies
make run         # starts the dashboard on http://localhost:8000
```

To use a different port:

```bash
make run PORT=3000
```

To clean up:

```bash
make clean
```

## Key Metrics

**Stability Score** -- `1 - RMS(corrected) / RMS(raw)` per finger. Higher means more tremor energy was removed. A realistic good result is 25-40%.

**Estimated Frequency** -- Dominant oscillation frequency in the detected tremor band, found via FFT. Clinically: 4-12 Hz for essential tremor, 4-6 Hz for Parkinson's.

**Correction Gain (K)** -- Multiplier for the inverse correction signal. K=1.0 is optimal (full cancellation). K<1 under-corrects, K>1 over-corrects and re-injects inverted tremor.

## Next Steps

- Adaptive gain that adjusts K based on amplitude and frequency stability
- Sliding-window real-time estimation instead of static 5-second windows
- ESP32 + IMU integration for physical sensor input
- Actuator output signal generation for hardware-in-the-loop testing
