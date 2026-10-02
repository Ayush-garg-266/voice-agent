"""
Q3 Offline MMS-TTS Audio Evidence Synthesis Utility.

Synthesizes native WAV audio recording evidence files for Philippines (Tagalog/Taglish)
and Indonesia (Javanese regional dialect) scenarios using Hugging Face Meta MMS-TTS models:
- facebook/mms-tts-tgl (Filipino / Tagalog)
- facebook/mms-tts-jav (Javanese)

REQUIREMENTS:
-------------
- transformers
- torch
- scipy

USAGE:
------
python q3_multilingual/speech/synthesize_mms_recordings.py

FFMPEG CONVERSION (Optional for MP3):
--------------------------------------
ffmpeg -y -i recordings/q3/ph_call_01_cooperative.wav -codec:a libmp3lame -qscale:a 2 recordings/q3/ph_call_01_cooperative.mp3
ffmpeg -y -i recordings/q3/ph_call_02_escalation.wav -codec:a libmp3lame -qscale:a 2 recordings/q3/ph_call_02_escalation.mp3
ffmpeg -y -i recordings/q3/id_call_02_regional.wav -codec:a libmp3lame -qscale:a 2 recordings/q3/id_call_02_regional.mp3
"""

import os
import sys
import json
import wave
from typing import List, Dict, Any, Tuple

# Prevent OpenMP duplicate runtime initialization crash on Windows Anaconda
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Fix Windows stdout encoding for Unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRANSCRIPT_DIR = os.path.join(ROOT_DIR, "q3_multilingual", "evaluation", "transcripts")
RECORDINGS_DIR = os.path.join(ROOT_DIR, "recordings", "q3")

SCENARIOS = [
    {
        "market": "Philippines",
        "scenario": "Cooperative Bancassurance Renewal",
        "source_transcript": "ph_01_cooperative.json",
        "output_filename": "ph_call_01_cooperative.wav",
        "model_id": "facebook/mms-tts-tgl",
        "language": "Tagalog / Taglish"
    },
    {
        "market": "Philippines",
        "scenario": "Human Escalation Request",
        "source_transcript": "ph_05_escalation.json",
        "output_filename": "ph_call_02_escalation.wav",
        "model_id": "facebook/mms-tts-tgl",
        "language": "Tagalog / Taglish"
    },
    {
        "market": "Indonesia",
        "scenario": "Regional Javanese Dialect Scenario",
        "source_transcript": "id_06_regional_accent.json",
        "output_filename": "id_call_02_regional.wav",
        "model_id": "facebook/mms-tts-jav",
        "language": "Javanese / Indonesian"
    }
]


def check_wav_info(file_path: str) -> Tuple[float, int, int]:
    """Returns (duration_seconds, sample_rate, byte_size) for a WAV file."""
    if not os.path.exists(file_path):
        return 0.0, 0, 0
    byte_size = os.path.getsize(file_path)
    try:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = round(frames / float(rate), 2)
            return duration, rate, byte_size
    except Exception:
        return 0.0, 0, byte_size


def check_dependencies() -> Tuple[bool, str]:
    """Verifies that transformers, torch, and scipy are available."""
    missing = []
    try:
        import torch
    except ImportError:
        missing.append("torch")
    try:
        import transformers
    except ImportError:
        missing.append("transformers")
    try:
        import scipy
    except ImportError:
        missing.append("scipy")

    if missing:
        cmd = f"pip install {' '.join(missing)}"
        return False, f"Missing dependencies: {', '.join(missing)}. Please run: {cmd}"
    return True, "All dependencies present"


def synthesize_scenario_mms(config: Dict[str, Any], overwrite: bool = False) -> Tuple[bool, str, float, int, int]:
    """
    Synthesizes exact transcript dialogue into a native WAV file using Meta MMS-TTS.
    """
    source_path = os.path.join(TRANSCRIPT_DIR, config["source_transcript"])
    output_path = os.path.join(RECORDINGS_DIR, config["output_filename"])

    if not os.path.exists(source_path):
        return False, f"Transcript missing: {config['source_transcript']}", 0.0, 0, 0

    if os.path.exists(output_path) and not overwrite:
        duration, rate, size = check_wav_info(output_path)
        if size > 10240 and duration > 0:
            return True, "EXISTS (Skipped - pass --overwrite to force)", duration, rate, size

    try:
        import torch
        from transformers import VitsModel, AutoTokenizer
        import scipy.io.wavfile
    except Exception as e:
        return False, f"DEPENDENCY ERROR: {e}", 0.0, 0, 0

    # Load transcript turns
    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript_turns = data.get("transcript", [])
    if not transcript_turns:
        return False, "ERROR: Empty transcript", 0.0, 0, 0

    # Collect exact turn texts
    dialogue_lines = []
    for turn in transcript_turns:
        u_text = turn.get("user", "").strip()
        b_text = turn.get("bot", "").strip()
        if u_text:
            dialogue_lines.append(u_text)
        if b_text:
            dialogue_lines.append(b_text)

    full_text = " ".join(dialogue_lines)

    # Load Hugging Face MMS-TTS model & tokenizer
    try:
        print(f"   Loading Hugging Face model {config['model_id']} ...")
        model = VitsModel.from_pretrained(config["model_id"])
        tokenizer = AutoTokenizer.from_pretrained(config["model_id"])
    except Exception as e:
        return False, f"MODEL LOAD ERROR ({config['model_id']}): {e}", 0.0, 0, 0

    # Perform CPU inference
    try:
        import numpy as np
        inputs = tokenizer(full_text, return_tensors="pt")
        with torch.no_grad():
            output = model(**inputs).waveform

        waveform = output.squeeze().cpu().numpy()
        sampling_rate = model.config.sampling_rate

        # Scale float32 [-1.0, 1.0] waveform to 16-bit PCM int16 format
        waveform_int16 = (waveform * 32767.0).clip(-32768, 32767).astype(np.int16)

        os.makedirs(RECORDINGS_DIR, exist_ok=True)
        scipy.io.wavfile.write(output_path, rate=sampling_rate, data=waveform_int16)
    except Exception as e:
        return False, f"INFERENCE ERROR: {e}", 0.0, 0, 0

    duration, rate, size = check_wav_info(output_path)
    if size > 10240 and duration > 0:
        return True, "SUCCESS", duration, rate, size
    else:
        return False, "VERIFICATION FAILED: Invalid output WAV", duration, rate, size


def run_synthesis(overwrite: bool = False):
    """Executes MMS-TTS synthesis for Philippines and Indonesian regional audio evidence."""
    print("\n==================================================")
    print("  Q3 META MMS-TTS AUDIO EVIDENCE SYNTHESIS UTILITY")
    print("==================================================\n")

    dep_ok, dep_msg = check_dependencies()
    if not dep_ok:
        print(f"❌ {dep_msg}\n")
        sys.exit(1)

    results = []

    for config in SCENARIOS:
        print(f"Synthesizing [{config['market']}] ({config['language']}) -> {config['output_filename']} ...")
        success, status, duration, rate, file_size = synthesize_scenario_mms(config, overwrite=overwrite)
        results.append({
            "filename": config["output_filename"],
            "source": config["source_transcript"],
            "market": config["market"],
            "model": config["model_id"],
            "size_kb": f"{round(file_size / 1024, 1)} KB",
            "sample_rate": f"{rate} Hz",
            "duration": f"{duration}s",
            "status": "PASS" if success else "FAIL (" + status + ")"
        })

    print("\n==================================================")
    print("         Q3 RECORDING EVIDENCE SYNTHESIS SUMMARY  ")
    print("==================================================\n")

    print(f"{'Filename':<30} | {'Model':<22} | {'Rate':<9} | {'Size':<9} | {'Duration':<8} | {'Status'}")
    print("-" * 95)
    for r in results:
        print(f"{r['filename']:<30} | {r['model']:<22} | {r['sample_rate']:<9} | {r['size_kb']:<9} | {r['duration']:<8} | {r['status']}")

    print("\nOutput directory: " + RECORDINGS_DIR + "\n")


if __name__ == "__main__":
    overwrite_flag = "--overwrite" in sys.argv
    run_synthesis(overwrite=overwrite_flag)
