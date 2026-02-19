"""
app.py — Sahaba Islamic Assistant Streamlit Frontend.

Supports three configurations:
  A — Text Only
  B — Text + Audio (TTS output, auto-play toggle, replay button)
  C — Full Multimodal (Voice input, Qibla compass, date picker, TTS)

Dark mode, premium design with Inter font and gold accents.
"""

import base64
import datetime
import io
import time

import requests
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent import create_agent, run_agent
from config import CONFIG_A, CONFIG_B, CONFIG_C, CONFIG_LABELS
from tts_stt import text_to_speech, speech_to_text

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sahaba — Islamic Assistant",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Dark Mode Styling ────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Root & Body ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}

/* ── Header ── */
.sahaba-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
}
.sahaba-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c8a96e 0%, #f0d090 50%, #c8a96e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
    margin: 0;
}
.sahaba-subtitle {
    color: #8b949e;
    font-size: 0.9rem;
    margin-top: 0.25rem;
    font-weight: 300;
    letter-spacing: 0.12em;
}
.bismillah {
    font-family: 'Amiri', serif;
    font-size: 1.5rem;
    color: #c8a96e;
    text-align: center;
    margin: 0.5rem 0 1.5rem;
    opacity: 0.9;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background-color: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stChatMessage"]:hover {
    border-color: #30363d !important;
}

/* Assistant messages — slightly different bg */
[data-testid="stChatMessage"][data-testid*="assistant"] {
    background-color: #1c2128 !important;
}

/* ── Sidebar widgets ── */
[data-testid="stSidebar"] label {
    color: #c8a96e !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stSidebar"] .stRadio label span {
    color: #e6edf3 !important;
    font-weight: 400 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #c8a96e, #a0824e) !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.2s, transform 0.1s !important;
    padding: 0.4rem 1.2rem !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Input box ── */
[data-testid="stChatInput"] textarea {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 2px rgba(200, 169, 110, 0.15) !important;
}

/* ── Config badge ── */
.config-badge {
    display: inline-block;
    background: rgba(200, 169, 110, 0.15);
    color: #c8a96e;
    border: 1px solid rgba(200, 169, 110, 0.3);
    border-radius: 20px;
    padding: 0.15rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

/* ── Arabic text ── */
.arabic-text {
    font-family: 'Amiri', serif !important;
    font-size: 1.4rem !important;
    direction: rtl !important;
    color: #f0d090 !important;
    line-height: 2.2 !important;
}

/* ── Audio player ── */
audio {
    width: 100%;
    border-radius: 8px;
    margin-top: 0.5rem;
    filter: invert(1) hue-rotate(180deg) brightness(0.9);
}

/* ── Divider ── */
hr {
    border-color: #21262d !important;
    margin: 1rem 0 !important;
}

/* ── Compass image ── */
.compass-container {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
}
.compass-container img {
    border-radius: 50%;
    border: 2px solid #c8a96e;
    max-width: 220px;
    box-shadow: 0 0 20px rgba(200, 169, 110, 0.2);
}

/* ── Toggle ── */
[data-testid="stToggle"] label {
    color: #8b949e !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3d444d; }

/* ── Date picker ── */
[data-testid="stDateInput"] input {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}

/* ── spinner ── */
[data-testid="stSpinner"] {
    color: #c8a96e !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def today_str() -> str:
    """Return today's date as DD-MM-YYYY."""
    return datetime.datetime.utcnow().strftime("%d-%m-%Y")


def audio_autoplay_html(audio_bytes: bytes) -> str:
    """Return an HTML audio element with autoplay from raw MP3 bytes."""
    b64 = base64.b64encode(audio_bytes).decode()
    return (
        f'<audio autoplay controls style="width:100%;border-radius:8px;margin-top:0.5rem;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        f'</audio>'
    )


def audio_manual_html(audio_bytes: bytes) -> str:
    """Return a plain HTML audio element (no autoplay)."""
    b64 = base64.b64encode(audio_bytes).decode()
    return (
        f'<audio controls style="width:100%;border-radius:8px;margin-top:0.5rem;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        f'</audio>'
    )


def extract_compass_url(text: str) -> tuple[str, str]:
    """Check if the agent response embeds a QIBLA_COMPASS_IMAGE marker.
    
    Returns (clean_text, compass_url_or_empty).
    """
    marker = "QIBLA_COMPASS_IMAGE:"
    if marker in text:
        parts = text.split(marker, 1)
        clean = parts[0].strip()
        url_part = parts[1].strip().split()[0]  # grab just the URL
        return clean, url_part
    return text, ""


def fetch_compass_image(url: str) -> bytes | None:
    """Fetch compass image bytes from the aladhan API."""
    try:
        print(f"[APP] Fetching compass image: {url}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"[APP] Compass image fetch failed: {e}")
        return None


def fetch_recitation_audio(audio_url: str) -> bytes | None:
    """Fetch recitation MP3 bytes from api.alquran.cloud CDN."""
    try:
        print(f"[APP] Fetching recitation audio: {audio_url}")
        resp = requests.get(audio_url, timeout=20)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"[APP] Recitation audio fetch failed: {e}")
        return None


# ─── Session State Initialisation ────────────────────────────────────────────

def _init_state():
    defaults = {
        "config_mode": CONFIG_A,
        "messages": [],           # LangChain message objects
        "display_turns": [],      # List of {"role", "content", "audio_bytes", "compass_url", "recitation_url"}
        "agent": None,
        "agent_config": None,
        "auto_play": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <span style="font-size: 2rem;">🌙</span>
        <p style="color:#c8a96e; font-weight:700; font-size:1.3rem; margin:0.25rem 0 0;">Sahaba</p>
        <p style="color:#8b949e; font-size:0.75rem; letter-spacing:0.1em;">ISLAMIC ASSISTANT</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Configuration selector
    st.markdown("**Configuration**")
    config_choice = st.radio(
        "Select mode",
        options=[CONFIG_A, CONFIG_B, CONFIG_C],
        format_func=lambda x: CONFIG_LABELS[x],
        index=[CONFIG_A, CONFIG_B, CONFIG_C].index(st.session_state.config_mode),
        label_visibility="collapsed",
    )

    # Reset agent if configuration changed
    if config_choice != st.session_state.config_mode:
        st.session_state.config_mode = config_choice
        st.session_state.agent = None
        st.session_state.messages = []
        st.session_state.display_turns = []
        st.rerun()

    st.markdown("---")

    # ── Audio controls (Config B and C)
    if st.session_state.config_mode in (CONFIG_B, CONFIG_C):
        st.markdown("**Audio Settings**")
        st.session_state.auto_play = st.toggle(
            "Auto-play TTS response",
            value=st.session_state.auto_play,
        )

    # ── Date picker (Config C)
    selected_date = None
    if st.session_state.config_mode == CONFIG_C:
        st.markdown("---")
        st.markdown("**Date**")
        selected_date = st.date_input(
            "Pick a date for prayer/calendar queries",
            value=datetime.datetime.utcnow(),
            label_visibility="collapsed",
        )

    st.markdown("---")

    # ── New Conversation button
    if st.button("🔄  New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.display_turns = []
        st.session_state.agent = None
        st.rerun()

    # ── Config info
    st.markdown("---")
    mode = st.session_state.config_mode
    info = {
        CONFIG_A: "📝 Text only — no audio output",
        CONFIG_B: "🔊 Text + TTS audio output",
        CONFIG_C: "🎤 Full multimodal — voice in, compass, audio",
    }
    st.markdown(f"<small style='color:#8b949e;'>{info[mode]}</small>", unsafe_allow_html=True)


# ─── Main Panel ───────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="sahaba-header">
    <h1 class="sahaba-title">🌙 Sahaba</h1>
    <p class="sahaba-subtitle">YOUR ISLAMIC COMPANION</p>
</div>
<p class="bismillah">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</p>
""", unsafe_allow_html=True)

# Config badge
mode_label = CONFIG_LABELS[st.session_state.config_mode]
st.markdown(
    f'<div style="text-align:center;margin-bottom:1.5rem;">'
    f'<span class="config-badge">Config {mode_label}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Build / retrieve agent (cached in session) ─────────────────────────────

if st.session_state.agent is None or st.session_state.agent_config != st.session_state.config_mode:
    print(f"\n[APP] Building agent for config={st.session_state.config_mode}")
    with st.spinner("Initialising Sahaba…"):
        st.session_state.agent = create_agent(
            config_mode=st.session_state.config_mode,
            today=today_str(),
        )
        st.session_state.agent_config = st.session_state.config_mode


# ── Render existing conversation turns ────────────────────────────────────

for turn in st.session_state.display_turns:
    role = turn["role"]
    with st.chat_message(role, avatar="🧑" if role == "user" else "🌙"):
        content = turn["content"]

        # Render Arabic text with special class if detected (right-to-left block)
        if "**" in content and any(
            "\u0600" <= c <= "\u06ff" for c in content
        ):
            # Mixed Arabic/English — let markdown handle bold
            st.markdown(content)
        else:
            st.markdown(content)

        # Compass image (Config C)
        if turn.get("compass_bytes"):
            st.markdown('<div class="compass-container">', unsafe_allow_html=True)
            st.image(turn["compass_bytes"], caption="Qibla Compass", width=220)
            st.markdown('</div>', unsafe_allow_html=True)

        # Recitation audio player
        if turn.get("recitation_bytes") and st.session_state.config_mode in (CONFIG_B, CONFIG_C):
            st.markdown("**🎧 Quranic Recitation:**")
            html = audio_manual_html(turn["recitation_bytes"])
            st.markdown(html, unsafe_allow_html=True)

        # TTS audio (Config B/C)
        if turn.get("audio_bytes") and role == "assistant" and st.session_state.config_mode in (CONFIG_B, CONFIG_C):
            st.markdown("**🔊 Audio Response:**")
            st.markdown(audio_manual_html(turn["audio_bytes"]), unsafe_allow_html=True)


# ── Voice Input (Config C only) ───────────────────────────────────────────

voice_transcript = None
if st.session_state.config_mode == CONFIG_C:
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        voice_file = st.file_uploader(
            "🎤 Upload voice message",
            type=["mp3", "mp4", "wav", "m4a", "webm", "ogg"],
            label_visibility="collapsed",
            key="voice_uploader",
        )
    with col2:
        st.markdown(
            "<small style='color:#8b949e; line-height:2.5;'>Upload an audio file to speak to Sahaba</small>",
            unsafe_allow_html=True,
        )

    if voice_file is not None:
        audio_bytes = voice_file.read()
        with st.spinner("Transcribing audio…"):
            voice_transcript = speech_to_text(audio_bytes, filename=voice_file.name)
        st.success(f"🎤 You said: *{voice_transcript}*")


# ── Text Chat Input ────────────────────────────────────────────────────────

prompt_placeholder = {
    CONFIG_A: "Ask about Quran, prayer times, Islamic calendar… (include your location if needed)",
    CONFIG_B: "Ask about Quran, prayer times, Islamic calendar… (include your location if needed)",
    CONFIG_C: "Ask me anything — or use the voice uploader above ✨",
}[st.session_state.config_mode]

user_input = st.chat_input(prompt_placeholder)

# Use voice transcript if available and no text typed
final_input = voice_transcript if (voice_transcript and not user_input) else user_input

# Inject selected date if Config C and date was chosen
if final_input and st.session_state.config_mode == CONFIG_C and selected_date:
    date_str = selected_date.strftime("%d-%m-%Y")
    if date_str not in final_input:
        final_input = f"[Date context: {date_str}] {final_input}"


# ── Process input ──────────────────────────────────────────────────────────

if final_input:
    print(f"\n[APP] User input received (config={st.session_state.config_mode}): {final_input[:200]}")

    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(final_input)

    st.session_state.display_turns.append({
        "role": "user",
        "content": final_input,
    })

    # Run agent
    with st.chat_message("assistant", avatar="🌙"):
        with st.spinner("Sahaba is thinking…"):
            ai_text, updated_messages = run_agent(
                graph=st.session_state.agent,
                messages=st.session_state.messages,
                user_input=final_input,
            )
            st.session_state.messages = updated_messages

        # Check for Qibla compass marker in response
        clean_text, compass_url = extract_compass_url(ai_text)

        # Check for recitation URL in response
        recitation_url = ""
        recitation_marker = "Recitation audio URL for"
        recitation_bytes = None
        if recitation_marker in clean_text and "http" in clean_text:
            # Extract URL from text
            import re
            url_match = re.search(r'https?://\S+\.mp3', clean_text)
            if url_match:
                recitation_url = url_match.group(0)

        # Render AI text
        st.markdown(clean_text)

        # Fetch and show compass image (Config C)
        compass_bytes = None
        if compass_url and st.session_state.config_mode == CONFIG_C:
            with st.spinner("Loading Qibla compass…"):
                compass_bytes = fetch_compass_image(compass_url)
            if compass_bytes:
                st.markdown('<div class="compass-container">', unsafe_allow_html=True)
                st.image(compass_bytes, caption="Qibla Compass", width=220)
                st.markdown('</div>', unsafe_allow_html=True)

        # Fetch and show recitation audio (Config B/C)
        if recitation_url and st.session_state.config_mode in (CONFIG_B, CONFIG_C):
            with st.spinner("Loading recitation audio…"):
                recitation_bytes = fetch_recitation_audio(recitation_url)
            if recitation_bytes:
                st.markdown("**🎧 Quranic Recitation:**")
                st.markdown(audio_manual_html(recitation_bytes), unsafe_allow_html=True)

        # Generate TTS audio (Config B/C)
        tts_bytes = None
        if st.session_state.config_mode in (CONFIG_B, CONFIG_C) and clean_text.strip():
            with st.spinner("Generating audio response…"):
                try:
                    # Strip Arabic text from TTS input for cleaner speech
                    import re as _re
                    tts_text = _re.sub(r'[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+', '', clean_text)
                    tts_text = tts_text.strip()[:1000]  # cap at 1000 chars for TTS
                    if tts_text:
                        tts_bytes = text_to_speech(tts_text)
                except Exception as e:
                    print(f"[APP] TTS failed: {e}")

            if tts_bytes:
                st.markdown("**🔊 Audio Response:**")
                if st.session_state.auto_play:
                    st.markdown(audio_autoplay_html(tts_bytes), unsafe_allow_html=True)
                else:
                    st.markdown(audio_manual_html(tts_bytes), unsafe_allow_html=True)

    # Store turn for re-render
    st.session_state.display_turns.append({
        "role": "assistant",
        "content": clean_text,
        "audio_bytes": tts_bytes,
        "compass_bytes": compass_bytes,
        "recitation_bytes": recitation_bytes,
    })

    # Clear voice uploader after processing
    if voice_transcript:
        st.rerun()
