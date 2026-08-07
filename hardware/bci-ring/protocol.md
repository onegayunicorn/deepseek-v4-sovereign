# SOVEREIGN BCI Ring — BLE GATT & Packet Protocol

> Revision 1.0 · BLE 5.0 · Privacy-first: raw waveforms are opt-in only.
> Brand: **SOVEREIGN** · `#00E5FF` cyan accents on `#0A0A10`.

## 1. GATT Service Layout

**Service base UUID:** `0000xxxx-89ab-cdef-0123-456789abcdef` (128-bit, little-endian on air).

One primary service carries all ring characteristics. The 16-bit `xxxx` slot identifies
the characteristic as listed below.

### Service `0000SVR1-89ab-cdef-0123-456789abcdef` — `Sovereign BCI Ring Service`

| Characteristic | UUID (`xxxx`) | Properties | Format | Direction | Notes |
|---|---|---|---|---|---|
| `eeg_stream`  | `0xEE01` | NOTIFY | 20-byte packet | Ring → Host | 4-ch feature block, 20 Hz |
| `ppg_stream`  | `0xEE02` | NOTIFY | 20-byte packet | Ring → Host | HR/HRV/SpO₂ block, 20 Hz |
| `imu_stream`  | `0xEE03` | NOTIFY | 20-byte packet | Ring → Host | accel/gyro block, 25 Hz |
| `command`     | `0xEE04` | WRITE, NOTIFY | 1–16 byte CMD | Bidirectional | control + raw-waveform opt-in |
| `battery`     | `0xEE05` | READ, NOTIFY | 2 bytes | Ring → Host | SOC % + mV, notify on change |
| `device_info` | `0xEE06` | READ | ASCII string | Ring → Host | model, fw, serial |

All NOTIFY characteristics carry a **CCC descriptor** (`0x2902`) and use **no
indications** (fire-and-forget streaming, avoids link-layer ACK stalls).

### Command characteristic (0xEE04) — request codes

| Code | Name | Payload | Meaning |
|---|---|---|---|
| `0x01` | `START_STREAM` | `[flags]` | Begin notify streams; bit0 EEG, bit1 PPG, bit2 IMU |
| `0x02` | `STOP_STREAM` | — | Suspend all notify streams |
| `0x03` | `SET_RATE` | `[eeg_hz][ppg_hz][imu_hz]` | Change sampling rates (250–500 / 50–100 / 100–200) |
| `0x04` | `ENABLE_RAW` | `[0|1]` | **Opt-in** raw waveform export (user-consented) |
| `0x05` | `LED_TEST` | `[0|1]` | Drive status LEDs (cyan/mint pulse) |
| `0x06` | `OTA_BEGIN` | 16-byte image header | Start DFU handshake (reserved, v1.1) |
| `0x7F` | `ACK` / `NACK` | `[code]` | Response to last command (notified) |

## 2. Packet Format

Every streamed packet is **exactly 20 bytes** (one BLE ATT payload) and is self-describing
so the host can demux without service state.

```
Byte 0        : header  = 0x53 ('S') fixed sync byte
Byte 1        : seq     = sequence number (rolls 0..255)
Byte 2        : type    = 0x01 EEG | 0x02 PPG | 0x03 IMU | 0x04 INFO
Byte 3        : flags   = bit7 raw|opt-in, bit6 sample-block-complete, bits5..0 reserved
Byte 4..17    : payload = 14 bytes of sensor payload (little-endian)
Byte 18..19   : crc16   = CCITT-FALSE over bytes 0..17
```

- **Multi-block grouping:** payloads carry *grouped samples*. The ring accumulates
  `N` consecutive samples into one block and marks the last packet of the block with
  `flags.bit6 = 1`. The host flushes its DSP frame only on that boundary.
- **Sequence:** monotonically increasing per stream type; a gap in `seq` signals a dropped
  packet (host may interpolate or flag).

### 2.1 EEG payload (type `0x01`, 14 bytes, 20 Hz → 500 SPS in 25-sample blocks)

```
bytes 4..11  : band powers, float32 ×2 → actually packed as u16 fixed-point ×4:
               theta(0..4095) alpha(0..4095) beta(0..4095) gamma(0..4095)  (8 bytes)
bytes 12..15 : block metrics: blink_count(u8), quality(u8), rms_uV(u16)      (4 bytes)
bytes 16..17 : sample_index within block (u16)                               (2 bytes)
```
4-byte float band powers would exceed 20 B, so fixed-point u16 scaling is used:
`value = raw_u16 / 4095 * full_scale_uV`. Raw 24-bit waveforms (opt-in) stream at
4 ch × 3 B = 12 B per sample, grouped 1 sample/packet with `flags.bit7 = 1`.

### 2.2 PPG payload (type `0x02`, 14 bytes, 20 Hz → 100 SPS in 5-sample blocks)

```
bytes 4..7   : hr_bpm u16 (0.01 BPM fixed), hrv_ms u16 (0.01 ms fixed)       (4 bytes)
bytes 8..9   : spo2 u16 (0.01 % fixed)                                        (2 bytes)
bytes 10..13 : ir_baseline u32 (moving 4 s DC average, 0.5 nA LSB)           (4 bytes)
bytes 14..15 : confidence u8 + wave_quality u8                                (2 bytes)
bytes 16..17 : sample_index within block (u16)                               (2 bytes)
```

### 2.3 IMU payload (type `0x03`, 14 bytes, 25 Hz → 200 SPS in 8-sample blocks)

```
bytes 4..9   : accel_x/y/z int16 (mg, 16 g full scale → 0.488 mg/LSB)         (6 bytes)
bytes 10..15 : gyro_x/y/z int16 (mdps, 2000 dps full scale → 61 µdps/LSB)     (6 bytes)
bytes 16..17 : sample_index within block (u16)                                (2 bytes)
```

### 2.4 Battery / info payloads

- `battery` (0xEE05, READ+NOTIFY): `[soc_u8 %][v_mv u16 LE]` → 3 bytes (padded to 20 if
  notified as packet type `0x04`).
- `device_info` (0xEE06, READ): UTF-8 `"SOVEREIGN-BCI-RING;fw=1.0.0;hw=1.0;sn=<12hex>"`.

## 3. Sample Grouping & Timing

| Stream | Sample rate | Samples/block | Block rate | Packet bytes |
|---|---|---|---|---|
| EEG | 500 SPS | 25 | 20 Hz | 20 |
| PPG | 100 SPS | 5 | 20 Hz | 20 |
| IMU | 200 SPS | 8 | 25 Hz | 20 |

The ring schedules acquisition on a 2 ms tick (500 Hz master clock) and packs blocks in
bursts right after the DRDY ISR, keeping sensor→BLE notify latency under **20 ms**.

## 4. Connection Parameters (Preferred)

| Parameter | Value | Rationale |
|---|---|---|
| Connection interval | 7.5 ms | 25 Hz × 20 B needs ≥ ~4 notify slots/s — plenty of headroom |
| Slave latency | 0 | Latency target < 20 ms |
| Supervision timeout | 4 s | Robust to brief RF loss |
| PHY | 2M (fallback 1M) | 20 B packets; 2M saves radio duty |
| TX power | 0 dBm default, 4 dBm boost for far-field | Balance battery vs range |
| MTU | 247 (negotiated) | Allows future bulk raw export over one notify batch |
| Notify pacing | ≤ 4 per connection event | Keeps link balanced |

## 5. Security & Privacy

1. **Pairing:** LE Secure Connections with bonding; numeric comparison on first connect.
2. **Raw waveform opt-in:** `ENABLE_RAW` (0x04) requires an *explicit host-side grant*;
   the ring defaults to `0` after every power cycle.
3. **No raw data by default:** only fixed-point band powers / metrics / IMU features leave
   the ring. Raw 24-bit EEG leaves only while `ENABLE_RAW = 1` and stops 30 s after the
   last grant refresh.
4. **Whitening:** link-layer encryption (AES-CCM) is mandatory once bonded.

## 6. Reference (host side)

The host implementation of this protocol is `BciRingAdapter` in
[`driver_adapter.py`](driver_adapter.py); it demuxes by `type` and yields
`dict`-style packets to the Sovereign OS ingest layer.
