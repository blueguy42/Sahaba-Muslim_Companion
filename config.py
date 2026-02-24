"""
config.py — Central configuration for Sahaba Islamic Assistant.
All API keys, model names, and base URLs are defined here.
"""

import os

# ─── OpenAI API Key ───────────────────────────────────────────────────────────
_key_file = os.path.join(os.path.dirname(__file__), "openai.key")
with open(_key_file, "r") as f:
    OPENAI_API_KEY = f.read().strip()

# ─── OpenAI Model Names ───────────────────────────────────────────────────────
CHAT_MODEL = "gpt-5-nano-2025-08-07"
TTS_MODEL = "gpt-4o-mini-tts"
STT_MODEL = "gpt-4o-mini-transcribe"
TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer

# ─── External API Base URLs ───────────────────────────────────────────────────
QURAN_API_BASE = "https://api.alquran.cloud/v1"
ALADHAN_API_BASE = "https://api.aladhan.com/v1"
GEOCODING_API_BASE = "https://nominatim.openstreetmap.org/search"
GEOCODING_USER_AGENT = "SahabaIslamicAssistant/1.0"

# ─── Configuration Modes ──────────────────────────────────────────────────────
CONFIG_A = "A"  # Text-only
CONFIG_B = "B"  # Text + Audio
CONFIG_C = "C"  # Full Multimodal

CONFIG_LABELS = {
    CONFIG_A: "A — Text Only",
    CONFIG_B: "B — Text & Audio Output",
    CONFIG_C: "C — Full Multimodal",
}
