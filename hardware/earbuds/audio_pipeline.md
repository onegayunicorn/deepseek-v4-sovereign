# SOVEREIGN AI Earbuds — Audio Signal Chain & Latency Budget

> Revision 1.0 · Brand: **SOVEREIGN** · `#00FFCC` mint highlights on `#0A0A10`.
> Companion doc to [`specs.yaml`](specs.yaml) and [`firmware/main.c`](firmware/main.c).

## 1. Signal Chain Overview

```
┌──────────────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────────────────────┐   ┌────────┐
│ mic array    │──►│ AEC │──►│ NR  │──►│ VAD │──►│ on-device inference  │──►│ BLE    │──► Sovereign OS
│ L/R + bone   │   │     │   │     │   │     │   │ (wake-word + tiny    │   │ LE     │
└──────────────┘   └─────┘   └─────┘   └─────┘   │  ASR / vocal feats)  │   │ Audio  │
                                                  └─────────────────────┘   └────────┘
                                                          │
        in-ear PPG ──► HR/HRV ──┐                        (feature packets, GATT)
        temp ────────► skin temp ┼──► biometric fusion ──► BLE GATT (5 s period)
        IMU ─────────► head pose ┘          │
                                           spatial audio renderer (local)
```

### Stage descriptions

1. **Mic array capture** — 2× MEMS ENC mics + 1× bone-conduction mic feed the QCC5171
   codec at 48 kHz / 24-bit in 128-sample frames (2.7 ms). The bone-conduction channel
   rides on accelerometer-coupled transduction, immune to ambient acoustic noise.
2. **AEC (Acoustic Echo Cancellation)** — full-duplex echo cancellation against the
   loudspeaker reference; required for any hands-free voice path and for on-device ASR
   robustness. Hybrid feedforward+feedback topology shared with ANC.
3. **Noise reduction (NR)** — spectral-subtraction + deep-learning noise suppression on
   the DSP. ENC beamformer steers toward the wearer's mouth using the bone-conduction
   reference for voice-activity weighting.
4. **VAD (Voice Activity Detection)** — energy + harmonic + bone-conduction fused
   detector. Gates all upstream inference to save power (inference duty ≈ 3 %).
5. **On-device inference** —
   - *Wake-word:* always-listening keyword spotter (e.g. "Hey Sovereign"), 100 % local.
   - *Tiny ASR:* whisper-class distilled model (~20–40 M params, int8 quantized) for
     short command recognition and dictation of brief utterances.
   - *Vocal biomarkers:* F0 jitter, spectral tilt, MFCCs extracted locally and shipped as
     compact feature vectors (no raw audio leaves the bud by default).
6. **Compression & streaming** — LC3 (LE Audio) or aptX Lossless/LDAC for the audio
   stream to the phone; biometric + biomarker features go over a parallel GATT link to
   Sovereign OS. Raw audio upload to Sovereign OS only after explicit wake-word + user
   consent.

## 2. Latency Budget (total < 150 ms)

| # | Stage | Budget (ms) | Cumulative (ms) | Notes |
|---|---|---|---|---|
| 1 | Mic capture + ADC (128 @ 48 kHz) | 2.7 | 2.7 | Frame-aligned DMA |
| 2 | AEC + echo reference align | 1.5 | 4.2 | Block-wise processing |
| 3 | Noise reduction + ENC beamform | 4.0 | 8.2 | Hybrid NN + spectral |
| 4 | VAD decision | 1.0 | 9.2 | 5 ms lookahead window |
| 5 | Wake-word / ASR inference | 40.0 | 49.2 | On-device int8 NN |
| 6 | Feature + audio pack | 2.0 | 51.2 | DMA double-buffer |
| 7 | BLE LE Audio ISOC transmit | 10.0 | 61.2 | 10 ms ISO interval, 1 slot |
| 8 | Jitter buffer + decode (host) | 20.0 | 81.2 | Host-side Slack |
| — | Head-tracking → spatial render (local) | 20.0 | 101.2 | Parallel path, not serial |
| — | **Design ceiling** | — | **150** | Includes OS scheduling & RF retries |

- The **voice-assist path** (mic → Sovereign OS) meets ≈ 62 ms; the
  **playback path** (local media + spatial audio) runs entirely on-device at ≈ 20 ms.
- The **150 ms ceiling** is the contract Sovereign OS can rely on for UX (transcription
  display, assistant turn-taking). Any stage exceeding its budget by > 2× triggers a
  quality-of-service event to the host (adaptive bitrate drop / ANC bypass).

## 3. On-Device Inference Details

| Model | Purpose | Size (int8) | Latency target |
|---|---|---|---|
| Wake-word spotter ("Hey Sovereign") | Gating + activation | 0.5 MB | ≤ 25 ms |
| Tiny ASR (whisper-class distilled, 4-layer) | Commands / short dictation | 4.5 MB | ≤ 150 ms per 2 s clip |
| Vocal biomarker net | F0 jitter, tilt, MFCC → emotion | 0.8 MB | ≤ 30 ms per 100 ms frame |

Inference runs on the application core while the audio core handles codec + ANC, with
shared SRAM banking. Model weights live in the 32 MB QSPI flash, mapped read-only.

## 4. Biometric Fusion

Every 5 s the bud publishes a **biometric frame** over GATT:

```
frame = {
  hr_bpm, hrv_ms, spo2,            # in-ear PPG (MAX30102-class)
  skin_temp_c,                     # NTC thermistor
  head_yaw/pitch/roll,             # IMU-derived
  vocal: { f0_jitter, tilt, mfcc_13, emotion },   # from vocal_analyzer
  battery_soc_per_bud
}
```

Fusion follows the [`msecr_framework.py`](../../../sensors/msecr_framework.py) pattern
referenced by the Sovereign OS analytics layer; the bud only ships features, never raw
waveforms.

## 5. Power-Saving Rules

1. VAD off → audio DSP enters 1.2 ms-frame sleep between frames.
2. Wake-word passes → tiny ASR boots (cold start < 80 ms).
3. Bud in case (pogo connected) → deep sleep, charger managed by case.
4. No BT link for 10 min → advertising off; wake on in-ear wear detection (PPG touch).
