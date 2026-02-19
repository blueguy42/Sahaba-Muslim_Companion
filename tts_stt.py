"""
tts_stt.py — Text-to-Speech and Speech-to-Text via OpenAI for Sahaba.

Uses:
  - gpt-4o-mini-tts  : Text → MP3 audio bytes
  - gpt-4o-mini-transcribe : Audio bytes → transcript text
"""

import io
import tempfile
import os
from openai import OpenAI
from config import OPENAI_API_KEY, TTS_MODEL, STT_MODEL, TTS_VOICE

client = OpenAI(api_key=OPENAI_API_KEY)


def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gpt-4o-mini-tts.
    
    Args:
        text: The text to synthesise into audio.
    
    Returns:
        MP3 audio as raw bytes.
    """
    print(f"\n[TTS] text_to_speech called")
    print(f"  Model: {TTS_MODEL}, Voice: {TTS_VOICE}")
    print(f"  Text ({len(text)} chars): {text[:120]}{'...' if len(text) > 120 else ''}")

    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="mp3",
    )
    audio_bytes = response.content
    print(f"  → Audio bytes received: {len(audio_bytes)} bytes")
    return audio_bytes


def speech_to_text(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio bytes to text using gpt-4o-mini-transcribe.
    
    Args:
        audio_bytes: Raw audio data (WebM/WAV/MP3/etc.)
        filename: Suggested filename with extension for format hint.
    
    Returns:
        Transcribed text string.
    """
    print(f"\n[STT] speech_to_text called")
    print(f"  Model: {STT_MODEL}, Audio size: {len(audio_bytes)} bytes")

    # Write to a temp file so the OpenAI SDK can handle the stream
    suffix = os.path.splitext(filename)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model=STT_MODEL,
                file=f,
            )
        text = transcript.text.strip()
        print(f"  → Transcript: {text[:200]}{'...' if len(text) > 200 else ''}")
        return text
    finally:
        os.unlink(tmp_path)
