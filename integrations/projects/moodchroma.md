# MoodChroma

**Role**: emotion · **Path**: `../moodchroma`

Biometric emotion pipeline: biometric intake, emotion relay, proactive
alerting.

## Integration surface

| Surface | Purpose |
|---|---|
| `biometric_pipeline.py` | Biometric data pipeline |
| `emotion_relay.py` | Emotion classification relay |
| `proactive_alert.py` | Proactive alerting |
| `moodchroma_engine.py` | Engine entry |

## Wiring into SOVEREIGN

- `moodchroma` agent (emotion capabilities) processes ring/earbuds
  biometrics through `hardware/` adapters.
- Emotion state can gate TTS voice response and proactive alerts.
