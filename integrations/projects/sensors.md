# Sensor Stack

**Role**: sensing · **Path**: `../sensors`

Physiological + environmental sensor processing: EEG, rPPG, thermal, touch,
tremor, vocal analysis, and the MSECR framework.

## Integration surface

| Surface | Purpose |
|---|---|
| `eeg_processor.py` | EEG processing (alpha/beta band power) |
| `rppg_sensor.py` | Remote photoplethysmography |
| `thermal_sensor.py` | Thermal sensing |
| `touch_telemetry.py` | Touch telemetry |
| `tremor_analyzer.py` | Tremor analysis |
| `vocal_analyzer.py` | Vocal analysis |
| `msecr_framework.py` | MSECR framework |

## Wiring into SOVEREIGN

- Ring adapter consumes `eeg_processor`; buds adapter consumes
  `vocal_analyzer` (both via defensive import in the hardware adapters).
- Sensor-fusion agent exposes the full capability set.
