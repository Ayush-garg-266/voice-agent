# Q3 Audio Recording Artifacts & Evidence Structure

This directory stores real audio recording evidence for Q3 SE Asian Multilingual Voice Bots (Philippines & Indonesia).

> [!IMPORTANT]
> In accordance with assessment constraints:
> - **No fabricated audio files**: Synthesized or live recorded `.mp3`/`.wav` audio files must be uploaded here from real call sessions or web voice bot tests.
> - **Transcripts**: Evaluated call transcripts are stored as structured JSON under `q3_multilingual/evaluation/transcripts/`.

## Structure & File Manifests

| Market | Recording File | Scenario | Audio Spec | Manifest File |
|---|---|---|---|---|
| **Philippines** | `ph_call_01_cooperative.mp3` | Bancassurance Renewal (Taglish) | 16kHz Mono MP3 | [`ph_call_01.manifest.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/ph_call_01.manifest.json) |
| **Philippines** | `ph_call_02_escalation.mp3` | Human Escalation (Taglish) | 16kHz Mono MP3 | [`ph_call_02.manifest.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/ph_call_02.manifest.json) |
| **Indonesia** | `id_call_01_cooperative.mp3` | Motor Loan Angsuran (Bahasa Indonesia) | 16kHz Mono MP3 | [`id_call_01.manifest.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/id_call_01.manifest.json) |
| **Indonesia** | `id_call_02_regional.mp3` | Regional Javanese Accent Dialect | 16kHz Mono MP3 | [`id_call_02.manifest.json`](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/recordings/q3/id_call_02.manifest.json) |

## Recording Procedure
To record live call sessions:
1. Run `python q3_multilingual/evaluation/evaluate_q3.py` with audio capture enabled via Web Voice Interface.
2. Export captured audio stream to MP3/WAV format.
3. Save audio file under `recordings/q3/` matching the manifest metadata.
