# SOVEREIGN BCI Ring

> Neural ring — EEG / PPG / IMU biosensing in a 22 mm band.
> Brand: **SOVEREIGN** · Palette: `#0A0A10` (background) · `#00E5FF` (cyan) · `#00FFCC` (mint)

![status](https://img.shields.io/badge/status-engineering-brightgreen)

## Product Overview

The **SOVEREIGN BCI Ring** is a biometric neural interface worn on the finger. It fuses
three sensing modalities into a single continuous stream for the Sovereign OS:

| Modality | Sensor | Purpose |
|---|---|---|
| EEG | ADS1299 (4-channel) | Cortical electrical activity — attention, relaxation, cognitive load |
| PPG | MAX30102 | Heart rate, HRV, blood-oxygen (SpO₂) — autonomic state |
| IMU | BMI270 | Finger micro-motion, tremor proxy, gesture/micro-gesture detection |

All sensing is **captured and processed on-device**: the ring runs artifact rejection,
band-power extraction (θ/α/β/γ), and HR/HRV estimation locally. **No raw signal leaves the
device by default** — the host OS receives compact feature packets (band powers, HR, HRV,
motion features) over BLE 5.0. Raw waveform export exists only as an explicit,
user-consented opt-in (see `protocol.md`).

## Integration with the Existing Stack

This hardware references (does **not** modify) the shared driver and sensor layers:

- Driver bridge: [`qlb_arduino_driver`](../../../drivers/qlb_arduino_driver.h) — QLB I2C/GPIO
  bridge used for sensor bus bring-up and hardware-in-the-loop bring-up on Arduino-class MCUs.
- EEG processing: [`eeg_processor.py`](../../../sensors/eeg_processor.py) — `EEGProcessor`,
  `EEGConfig` — real-time band-pass filtering, Welch PSD, band-power extraction.
- Motion analytics: [`tremor_analyzer.py`](../../../sensors/tremor_analyzer.py) — tremor
  metrics derived from the BMI270 stream.
- Physiological analytics: [`rppg_sensor.py`](../../../sensors/rppg_sensor.py) — rPPG/HRV
  fusion from the MAX30102 channel.

The Python host-side bridge lives in [`driver_adapter.py`](driver_adapter.py) and follows the
same adapter pattern as the Muse/QLB wrappers.

## Key Specifications (summary)

| Parameter | Value |
|---|---|
| MCU | nRF52840 (64 MHz Cortex-M4F, 1 MB flash / 256 KB RAM) — BLE 5.0 capable |
| EEG | ADS1299, 4 channels, 500 SPS, 24-bit |
| PPG | MAX30102, 100 SPS (IR + Red) |
| IMU | BMI270, 200 SPS accel + gyro |
| Radio | BLE 5.0 (nRF52840), GATT notify, connection interval 7.5 ms |
| Battery | 80 mAh LiPo, Qi wireless + USB-C charging |
| Enclosure | 22 mm inner-diameter ring, IP67 |
| Latency | Sensor → BLE notify < 20 ms |

Full details: [`specs.yaml`](specs.yaml) · BLE layout & packets: [`protocol.md`](protocol.md)
· Firmware: [`firmware/main.c`](firmware/main.c) · Host adapter: [`driver_adapter.py`](driver_adapter.py)

## Privacy-First Data Flow

```
 ADS1299 ─┐
 MAX30102 ─┼─► on-device DSP ─► feature vector ─► BLE 5.0 notify ─► Sovereign OS
 BMI270  ─┘        │
                   ├── artifact rejection (blink / motion)
                   ├── band power θ α β γ (Welch PSD)
                   ├── HR / HRV / SpO₂
                   └── tremor & micro-motion features
 Raw-waveform export: opt-in only, via command characteristic, user-gated.
```

## Repository Layout

```
bci-ring/
├── README.md            # this file
├── specs.yaml           # hardware & firmware specification
├── protocol.md          # BLE GATT layout + packet format
├── firmware/
│   └── main.c           # embedded C firmware sketch
└── driver_adapter.py    # Python host-side adapter (BciRingAdapter)
```

## Licensing / Ownership

Part of the SOVEREIGN wearable line. All rights reserved. Firmware is a reference sketch —
production builds require the vendor SDKs (Nordic nRF5 SDK / Zephyr) and FCC/CE certification.
