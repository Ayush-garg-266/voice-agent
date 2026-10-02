"""
Q3 Multilingual Voice Bot Audio Synthesis Utility.

Synthesizes physical MP3 recording evidence files for Philippines and Indonesia
test scenarios using Google Cloud Text-to-Speech API.

GOOGLE CLOUD AUTHENTICATION SETUP:
----------------------------------
To run this utility, ensure Google Cloud authentication is configured:
1. Install the Google Cloud Text-to-Speech SDK:
   pip install google-cloud-texttospeech
2. Set up Application Default Credentials (ADC):
   gcloud auth application-default login
   OR set the environment variable:
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\\path\\to\\service_account.json"
3. Run this script:
   python q3_multilingual/speech/synthesize_recordings.py

INPUT TRANSCRIPTS:
- q3_multilingual/evaluation/transcripts/ph_01_cooperative.json
- q3_multilingual/evaluation/transcripts/ph_05_escalation.json
- q3_multilingual/evaluation/transcripts/id_01_cooperative.json
- q3_multilingual/evaluation/transcripts/id_06_regional_accent.json

OUTPUT FILES:
- recordings/q3/ph_call_01_cooperative.mp3
- recordings/q3/ph_call_02_escalation.mp3
- recordings/q3/id_call_01_cooperative.mp3
- recordings/q3/id_call_02_regional.mp3
"""

import os
import sys
import json
import struct
import shutil
import subprocess
from typing import List, Dict, Any, Tuple

# Fix Windows stdout encoding for Unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRANSCRIPT_DIR = os.path.join(ROOT_DIR, "q3_multilingual", "evaluation", "transcripts")
RECORDINGS_DIR = os.path.join(ROOT_DIR, "recordings", "q3")
MODELS_DIR = os.path.join(ROOT_DIR, "q3_multilingual", "speech", "models")

SCENARIO_CONFIGS = [
    {
        "market": "Philippines",
        "scenario": "Cooperative Bancassurance Renewal",
        "source_transcript": "ph_01_cooperative.json",
        "output_filename": "ph_call_01_cooperative.mp3",
        "primary_language_code": "fil-PH",
        "voice_name": "fil-PH-Neural2-D",
        "user_voice_name": "en-PH-Neural2-A"
    },
    {
        "market": "Philippines",
        "scenario": "Human Escalation Request",
        "source_transcript": "ph_05_escalation.json",
        "output_filename": "ph_call_02_escalation.mp3",
        "primary_language_code": "fil-PH",
        "voice_name": "fil-PH-Neural2-D",
        "user_voice_name": "en-PH-Neural2-A"
    },
    {
        "market": "Indonesia",
        "scenario": "Cooperative Multifinance Motor Loan",
        "source_transcript": "id_01_cooperative.json",
        "output_filename": "id_call_01_cooperative.mp3",
        "primary_language_code": "id-ID",
        "voice_name": "id-ID-Wavenet-A",
        "user_voice_name": "id-ID-Wavenet-D",
        "piper_model": os.path.join(MODELS_DIR, "id_ID-news_tts-medium.onnx")
    },
    {
        "market": "Indonesia",
        "scenario": "Regional Javanese Dialect Scenario",
        "source_transcript": "id_06_regional_accent.json",
        "output_filename": "id_call_02_regional.mp3",
        "primary_language_code": "id-ID",
        "voice_name": "id-ID-Wavenet-A",
        "user_voice_name": "id-ID-Wavenet-D",
        "piper_model": os.path.join(MODELS_DIR, "id_ID-news_tts-medium.onnx")
    }
]


def check_mp3_duration(file_path: str) -> float:
    """
    Estimates MP3 audio duration in seconds by parsing MPEG frame headers.
    Returns 0.0 if invalid or unparseable.
    """
    if not os.path.exists(file_path):
        return 0.0

    file_size = os.path.getsize(file_path)
    if file_size < 1024:
        return 0.0

    bitrate_table = {
        1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]
    }

    try:
        with open(file_path, "rb") as f:
            data = f.read(10000)

        offset = 0
        while offset < len(data) - 4:
            if data[offset] == 0xFF and (data[offset + 1] & 0xE0) == 0xE0:
                header = struct.unpack(">I", data[offset:offset + 4])[0]
                version_bits = (header >> 19) & 0x03
                layer_bits = (header >> 17) & 0x03
                bitrate_idx = (header >> 12) & 0x0F

                version = 1 if version_bits == 3 else 2
                if layer_bits == 1 and bitrate_idx in range(1, 15):
                    bitrate_kbps = bitrate_table[version][bitrate_idx]
                    total_seconds = (file_size * 8) / (bitrate_kbps * 1000)
                    return round(total_seconds, 2)
            offset += 1

        # Fallback estimation based on average 128kbps bitrate
        return round((file_size * 8) / (128 * 1000), 2)
    except Exception:
        return 0.0


def check_wav_duration(file_path: str) -> float:
    """Calculates WAV audio duration from RIFF header."""
    if not os.path.exists(file_path):
        return 0.0
    import wave
    try:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return round(frames / float(rate), 2)
    except Exception:
        return 0.0


def check_ffmpeg() -> bool:
    """Checks whether ffmpeg executable is available on PATH."""
    return shutil.which("ffmpeg") is not None


def check_gcp_credentials() -> bool:
    """Checks whether Google Cloud credentials or SDK are available."""
    try:
        from google.cloud import texttospeech
        return True
    except ImportError:
        return False


def synthesize_with_piper(config: Dict[str, Any], overwrite: bool = False) -> Tuple[bool, str, float, int]:
    """
    Synthesizes dialogue using local Piper TTS model to WAV, and converts to MP3 if ffmpeg is available.
    """
    source_path = os.path.join(TRANSCRIPT_DIR, config["source_transcript"])
    piper_model = config.get("piper_model", "")
    mp3_output_path = os.path.join(RECORDINGS_DIR, config["output_filename"])
    wav_output_path = os.path.splitext(mp3_output_path)[0] + ".wav"

    if not os.path.exists(source_path):
        return False, f"Transcript missing: {config['source_transcript']}", 0.0, 0

    if not os.path.exists(piper_model):
        return False, f"Piper model missing: {piper_model}", 0.0, 0

    if os.path.exists(mp3_output_path) and not overwrite:
        file_size = os.path.getsize(mp3_output_path)
        duration = check_mp3_duration(mp3_output_path)
        if file_size > 10240 and duration > 0:
            return True, "EXISTS (Skipped - pass --overwrite to force)", duration, file_size

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript_turns = data.get("transcript", [])
    if not transcript_turns:
        return False, "ERROR: Empty transcript", 0.0, 0

    # Build exact dialogue spoken text
    full_text_turns = []
    for turn in transcript_turns:
        u_text = turn.get("user", "").strip()
        b_text = turn.get("bot", "").strip()
        if u_text:
            full_text_turns.append(u_text)
        if b_text:
            full_text_turns.append(b_text)

    combined_text = " ".join(full_text_turns)

    os.makedirs(RECORDINGS_DIR, exist_ok=True)

    # Execute Piper CLI
    piper_bin = shutil.which("piper") or "piper"
    cmd = [piper_bin, "-m", piper_model, "-f", wav_output_path]

    try:
        res = subprocess.run(cmd, input=combined_text, text=True, capture_output=True, check=True)
    except Exception as e:
        return False, f"Piper Execution Failed: {e}", 0.0, 0

    if not os.path.exists(wav_output_path) or os.path.getsize(wav_output_path) < 10240:
        return False, "Piper output WAV invalid or empty", 0.0, 0

    wav_size = os.path.getsize(wav_output_path)
    wav_duration = check_wav_duration(wav_output_path)

    # Check for ffmpeg to convert to MP3
    if check_ffmpeg():
        try:
            ff_cmd = ["ffmpeg", "-y", "-i", wav_output_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_output_path]
            subprocess.run(ff_cmd, capture_output=True, check=True)
            mp3_size = os.path.getsize(mp3_output_path)
            mp3_duration = check_mp3_duration(mp3_output_path)
            return True, "SUCCESS (Piper + ffmpeg MP3)", mp3_duration, mp3_size
        except Exception as e:
            return False, f"ffmpeg conversion failed: {e}", wav_duration, wav_size
    else:
        status_msg = (
            f"WAV GENERATED ({round(wav_size / 1024, 1)} KB, {wav_duration}s). "
            f"NOTICE: ffmpeg is NOT installed on PATH; cannot convert WAV to MP3 automatically."
        )
        return False, status_msg, wav_duration, wav_size


def synthesize_scenario(config: Dict[str, Any], overwrite: bool = False, use_piper: bool = False) -> Tuple[bool, str, float, int]:
    """
    Synthesizes dialogue turns from transcript JSON into an MP3 audio file.
    """
    if use_piper or ("piper_model" in config and os.path.exists(config["piper_model"])):
        return synthesize_with_piper(config, overwrite=overwrite)

    source_path = os.path.join(TRANSCRIPT_DIR, config["source_transcript"])
    output_path = os.path.join(RECORDINGS_DIR, config["output_filename"])

    if not os.path.exists(source_path):
        return False, f"Transcript missing: {config['source_transcript']}", 0.0, 0

    if os.path.exists(output_path) and not overwrite:
        file_size = os.path.getsize(output_path)
        duration = check_mp3_duration(output_path)
        if file_size > 10240 and duration > 0:
            return True, "EXISTS (Skipped - pass --overwrite to force)", duration, file_size

    try:
        from google.cloud import texttospeech
    except ImportError:
        return False, "ERROR: google-cloud-texttospeech library not installed", 0.0, 0

    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        return False, f"AUTH ERROR: Could not initialize TTS Client: {e}", 0.0, 0

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript_turns = data.get("transcript", [])
    if not transcript_turns:
        return False, "ERROR: Empty transcript", 0.0, 0

    combined_audio = bytearray()

    for turn in transcript_turns:
        user_text = turn.get("user", "").strip()
        bot_text = turn.get("bot", "").strip()

        if user_text:
            s_input = texttospeech.SynthesisInput(text=user_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=config["primary_language_code"],
                name=config["user_voice_name"]
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                sample_rate_hertz=16000
            )
            try:
                resp = client.synthesize_speech(input=s_input, voice=voice, audio_config=audio_config)
                combined_audio.extend(resp.audio_content)
            except Exception as e:
                return False, f"TTS API ERROR (User Turn): {e}", 0.0, 0

        if bot_text:
            s_input = texttospeech.SynthesisInput(text=bot_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=config["primary_language_code"],
                name=config["voice_name"]
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                sample_rate_hertz=16000
            )
            try:
                resp = client.synthesize_speech(input=s_input, voice=voice, audio_config=audio_config)
                combined_audio.extend(resp.audio_content)
            except Exception as e:
                return False, f"TTS API ERROR (Bot Turn): {e}", 0.0, 0

    if len(combined_audio) < 10240:
        return False, "ERROR: Generated audio is smaller than 10 KB threshold", 0.0, len(combined_audio)

    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(combined_audio)

    final_size = os.path.getsize(output_path)
    duration = check_mp3_duration(output_path)

    if final_size > 10240 and duration > 0:
        return True, "SUCCESS", duration, final_size
    else:
        return False, "VERIFICATION FAILED: Invalid MP3 output", duration, final_size


def run_synthesis(overwrite: bool = False, target_scenario: str = None):
    """Executes audio evidence synthesis for scenario recording files."""
    print("\n==================================================")
    print("   Q3 AUDIO EVIDENCE SYNTHESIS UTILITY (GCP / PIPER) ")
    print("==================================================\n")

    results = []

    configs_to_run = SCENARIO_CONFIGS
    if target_scenario:
        configs_to_run = [c for c in SCENARIO_CONFIGS if target_scenario in c["source_transcript"] or target_scenario in c["output_filename"]]

    for config in configs_to_run:
        print(f"Synthesizing [{config['market']}] -> {config['output_filename']} ...")
        success, status, duration, file_size = synthesize_scenario(config, overwrite=overwrite)
        results.append({
            "filename": config["output_filename"],
            "source": config["source_transcript"],
            "market": config["market"],
            "scenario": config["scenario"],
            "size_kb": f"{round(file_size / 1024, 1)} KB",
            "duration": f"{duration}s",
            "status": "PASS" if success else "INFO/FAIL (" + status + ")"
        })

    print("\n==================================================")
    print("         Q3 RECORDING EVIDENCE SYNTHESIS SUMMARY  ")
    print("==================================================\n")

    print(f"{'Filename':<32} | {'Market':<12} | {'Size':<9} | {'Duration':<9} | {'Status'}")
    print("-" * 80)
    for r in results:
        print(f"{r['filename']:<32} | {r['market']:<12} | {r['size_kb']:<9} | {r['duration']:<9} | {r['status']}")

    print("\nOutput directory: " + RECORDINGS_DIR + "\n")


if __name__ == "__main__":
    overwrite_flag = "--overwrite" in sys.argv
    run_synthesis(overwrite=overwrite_flag)
