# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the voice assistant
uv run voice-assistant
# or
uv run python -m voice_assistant

# Run tests
uv run python tests/test_voice_assistant.py

# List audio devices
uv run python -c "import pyaudio; pa = pyaudio.PyAudio(); [print(f'[{i}] {pa.get_device_info_by_index(i)[\"name\"]}') for i in range(pa.get_device_count())]; pa.terminate()"
```

## Architecture

Real-time bidirectional voice assistant using Google Gemini Live API on Raspberry Pi with WM8960 sound card.

**Data flow:**
1. `AudioCapture` records 16kHz PCM from microphone via PyAudio callback
2. `VoiceAssistant._send_audio()` streams chunks to Gemini via WebSocket
3. `VoiceAssistant._receive_audio()` receives 24kHz PCM responses
4. `AudioPlayer.play_sync()` resamples 24kHz→16kHz and plays audio

**Key constraint:** WM8960 requires identical sample rates for simultaneous input/output, hence both use 16kHz (Gemini's 24kHz output is resampled via `resample_linear()`).

**Main classes:**
- `VoiceAssistant` (assistant.py): Orchestrates Gemini session, runs concurrent send/receive tasks
- `AudioCapture` (audio.py): Callback-based mic capture with thread-safe deque buffer
- `AudioPlayer` (audio.py): Synchronous playback with automatic resampling
- `AudioConfig`/`GeminiConfig` (config.py): Dataclass configurations

## Configuration

- API key: Set `GEMINI_API_KEY` in `.env` file
- Audio device: `input_device_index` and `output_device_index` in `AudioConfig` (default: 1 for WM8960)
- Model: `gemini-2.5-flash-native-audio-preview-12-2025` in `GeminiConfig`
