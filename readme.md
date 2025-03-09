# Multi-Provider-Interface

#### A Streamlit application that provides a chat interface supporting multiple AI providers (OpenAI and Anthropic) with configurable parameters and image upload capabilities.#

### Features

- Easy Switching Between Anthropic and OpenAI Models
- Chat With Images
- Streaming Responses
- Comprehensive Message logging
- Set the System (Anthropic) or Developer (OpenAI) message
- Configurable Parameters:
  - Max tokens
  - Temperature
  - Top P
  - Top K'
- Text To Audio Using OpenAI TTS API
- Audio File Playback
- Combine Multiple Audio Files
- Test Voices With Tongue Twister Presets
- 7 Different Voices (more to come soon)

### Requirements

- streamlit
- openai
- anthropic
- python-dotenv

### Environment Variables

The following environment variables are required:

- OPENAI_API_KEY
- ANTHROPIC_API_KEY

*the code expects the variables to be within a .env file within the root directory*

### Available Models

- OpenAI
- gpt-4o
- gpt-4o-mini

#### Anthropic

- Claude-3 Sonnet
- Claude-3 Haiku
- Claude-3 Opus
- Claude-3 Sonnet Previous
- Claude-3 Haiku Previous

### Usage

```zsh
pip install python-dotenv streamlit openai anthropic
touch .env
```

then within your `.env` file:

```.env
OPENAI_API_KEY = sk-your_openai_api_key_here
ANTHROPIC_API_KEY = sk-your_anthropic_api_key_here
```

#### Run the application:

```zsh
streamlit run main.py
```