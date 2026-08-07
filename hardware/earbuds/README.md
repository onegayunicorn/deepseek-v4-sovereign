# SOVEREIGN AI Earbuds

> True-wireless earbuds — spatial audio, voice capture, in-ear biometrics, edge inference.
> Brand: **SOVEREIGN** · Palette: `#0A0A10` (background) · `#00E5FF` (cyan) · `#00FFCC` (mint)

![status](https://img.shields.io/badge/status-engineering-brightgreen)

## Product Overview

The **SOVEREIGN AI Earbuds** are the audio + physiological companion to the Sovereign OS.
Each bud packs:

| Capability | Implementation |
|---|---|
| Spatial audio | Head-tracking via on-bud IMU + binaural render (QCC5171 DSP) |
| Voice capture | Dual-mic ENC (environmental noise cancellation) + bone-conduction mic |
| In-ear biometrics | In-ear PPG (heart rate / HRV) + skin-contact temperature |
| Edge inference | On-device wake-word, small ASR/whisper-class model, vocal biomarker extraction |
| Connectivity | BLE 5.3 + LE Audio to Sovereign OS; aptX Lossless / LDAC / AAC to phone |

Audio and voice are processed **on-device**: AEC → noise reduction → VAD → inference →
compression, with an end-to-end latency budget under **150 ms** (see
[`audio_pipeline.md`](audio_pipeline.md)).

## Integration with the Existing Stack

This hardware references (does **not** modify) the shared driver and sensor layers:

- Driver bridge: [`muse_driver`](../../../drivers/muse_driver.py) — `MuseDriverWrapper` /
  `EEGPacket` pattern reused for the bud's BLE audio + biometric streaming transport.
- Vocal biomarkers: [`vocal_analyzer.py`](../../../sensors/vocal_analyzer.py) —
  `VocalAnalyzer`, `VocalConfig` — F0 jitter, spectral tilt, MFCC emotion classification.
- Physiological analytics: [`rppg_sensor.py`](../../../sensors/rppg_sensor.py) — HR/HRV from
  the in-ear PPG channel; [`thermal_sensor.py`](../../../sensors/thermal_sensor.py) — core
  temperature proxy; [`msecr_framework.py`](../../../sensors/msecr_framework.py) — multi-sensor
  fusion framework for combined audio + biometric state estimation.

The Python host-side bridge lives in [`driver_adapter.py`](driver_adapter.py).

## Key Specifications (summary)

| Parameter | Value |
|---|---|
| DSP | Qualcomm QCC5171 (LE Audio, dual-core) — alt: BES2700 |
| Codecs | aptX Lossless, LDAC (990 kbps), AAC, SBC |
| Mics | 2× MEMS (ENC) + 1× bone-conduction |
| Biometrics | In-ear PPG (MAX30102-class), NTC skin temp |
| Motion | 6-axis IMU per bud (head tracking) |
| Radio | BLE 5.3, LE Audio (ISOC), dual-bud relay |
| Battery | 45 mAh per bud + 500 mAh case |
| Runtime | 8 h playback / 40 h with case |
| Ingress | IPX5 (sweat/rain) |
| Latency | audio pipeline < 150 ms end-to-end |

Full details: [`specs.yaml`](specs.yaml) · Signal chain: [`audio_pipeline.md`](audio_pipeline.md)
· Firmware: [`firmware/main.c`](firmware/main.c) · Host adapter: [`driver_adapter.py`](driver_adapter.py)

## Data Flow

```
mic L/R ─┐
AEC ─────┼─► NR ─► VAD ─► on-device inference ─► codec (LC3/aptX) ─► BLE 5.3 ─► Sovereign OS
BC mic ──┘                          │
in-ear PPG ─► HR/HRV ───────────────┴─► biometric features (BLE GATT)
temp ─────► skin temp
IMU ──────► head tracking ─► spatial audio renderer
```

Wake-word detection is 100 % on-device; audio leaves the bud only after explicit
wake/consent (privacy-first, same doctrine as the BCI Ring).

## Repository Layout

```
earbuds/
├── README.md            # this file
├── specs.yaml           # hardware & firmware specification
├── audio_pipeline.md    # signal chain + latency budget
├── firmware/
│   └── main.c           # embedded C firmware sketch
└── driver_adapter.py    # Python host-side adapter (SovereignBudsAdapter)
```

## Licensing / Ownership

Part of the SOVEREIGN wearable line. All rights reserved. Firmware is a reference sketch —
production builds require Qualcomm/BES vendor SDKs and FCC/CE certification.
