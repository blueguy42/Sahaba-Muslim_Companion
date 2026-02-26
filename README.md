# Sahaba — Islamic AI Assistant

<img width="1458" height="789" alt="image" src="https://github.com/user-attachments/assets/2b28d3b5-02f4-499e-8562-e5506bff39f0" />


A sophisticated Islamic assistant built with Streamlit and powered by OpenAI's GPT models. This application provides users with accurate Islamic information, prayer times, Qibla direction, Quranic verses, and more through an intuitive conversational interface.

## 🌟 Features

### Three Configuration Modes

- **Configuration A**: Text-only interface for basic Islamic queries
- **Configuration B**: Text + Audio output with TTS capabilities
- **Configuration C**: Full multimodal experience with voice input, Qibla compass, and interactive features

### Core Capabilities

- 📖 **Quranic References**: Access verses with both Arabic text and English translations
- 🕌 **Prayer Times**: Get accurate prayer schedules for any location worldwide
- 🧭 **Qibla Direction**: Find the direction to Mecca with compass visualization
- 📅 **Islamic Calendar**: Date conversion and Islamic calendar information
- 🎙️ **Voice Interaction**: Speech-to-text input and text-to-speech output
- 🌍 **Location Services**: Automatic geolocation and address geocoding

## 🚀 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Sahaba-Muslim_Companion
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**
   - Create a file named `openai.key` in the project root
   - Add your OpenAI API key to this file (one line, no quotes)

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

1. Open your browser to the Streamlit URL (typically `http://localhost:8501`)
2. Select your preferred configuration mode from the sidebar
3. Choose your interaction preferences (dark mode, audio settings, etc.)
4. Start asking questions about Islam, prayer times, or Quranic verses

### Example Queries

- "What are today's prayer times in London?"
- "Show me Surah Al-Fatiha"
- "What's the Qibla direction from New York?"
- "Convert today's date to Islamic calendar"

## 🏗️ Project Structure

```
Sahaba-Muslim_Companion/
├── app.py              # Main Streamlit application
├── agent.py            # LangGraph ReAct agent implementation
├── api_tools.py        # External API integration tools
├── config.py           # Configuration and API keys
├── tts_stt.py          # Text-to-speech and speech-to-text utilities
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🛠️ Technical Details

### AI Model

- **Language Model**: GPT-5-nano-2025-08-07 (via LangChain)
- **TTS**: GPT-4o-mini-tts with "alloy" voice
- **STT**: GPT-4o-mini-transcribe

### External APIs

- **Al-Quran Cloud API**: Quranic text and translations
- **Aladhan API**: Prayer times and Islamic calendar
- **OpenStreetMap Nominatim**: Geocoding services

### Key Libraries

- **Streamlit**: Web application framework
- **LangGraph**: Agent orchestration
- **LangChain**: LLM integration
- **OpenAI**: AI model access
- **Streamlit-Geolocation**: Location services

## 🎨 Design Features

- **Dark Mode**: Premium dark theme with gold accents
- **Responsive Design**: Optimized for desktop and mobile
- **Inter Font**: Clean, modern typography
- **Arabic Support**: Proper rendering of Arabic text
- **Intuitive UI**: User-friendly interface with collapsible sidebar

## 📚 Course Context

This project was developed as part of the **Designing AI Experiences** course at the University of Cambridge MPhil program. It demonstrates the integration of multiple AI modalities (text, voice, location) into a cohesive user experience focused on Islamic education and practice.

## 🤝 Contributing

This is a course project, but suggestions and feedback are welcome. Please create an issue or submit a pull request if you'd like to contribute improvements.

## 📄 License

This project is developed for educational purposes as part of a university course. Please respect Islamic content copyrights and API usage terms.
