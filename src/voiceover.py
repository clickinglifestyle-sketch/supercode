import re
from pathlib import Path
from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL_ID,
    AUDIO_OUTPUT_DIR,
)


def _extract_narration(script_text: str, slot: str) -> str:
    """Pull the narration section from a Short production package, or return the full text for long-form."""
    if slot == "sun_longform":
        return script_text.strip()

    # Shorts: extract everything between "SCRIPT:" and the next section header
    match = re.search(r"SCRIPT:\s*\n(.*?)(?:\n[A-Z][A-Z\s]+—|\Z)", script_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return script_text.strip()


def generate_voiceover(script_text: str, case_id: str, slot: str) -> Path:
    """
    Send narration to ElevenLabs TTS and save the mp3.
    Returns the path to the saved audio file.
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not set. Add it to your .env file.")

    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings
    except ImportError:
        raise ImportError("elevenlabs package not installed. Run: pip install elevenlabs>=1.0.0")

    narration = _extract_narration(script_text, slot)
    if not narration:
        raise ValueError("Could not extract narration from script.")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio_iter = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=narration,
        model_id=ELEVENLABS_MODEL_ID,
        voice_settings=VoiceSettings(
            stability=0.45,
            similarity_boost=0.80,
            style=0.30,
            use_speaker_boost=True,
        ),
    )

    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = AUDIO_OUTPUT_DIR / f"{case_id}_{slot}.mp3"

    with open(out_path, "wb") as f:
        for chunk in audio_iter:
            f.write(chunk)

    return out_path
