from dataclasses import dataclass


@dataclass
class AudioConfig:
    """Audio configuration for microphone input and speaker output."""
    send_sample_rate: int = 16000      # Input sample rate (mic) - Gemini expects 16kHz
    receive_sample_rate: int = 24000   # Output sample rate from Gemini (24kHz)
    playback_sample_rate: int = 16000  # Actual playback rate (must match input for WM8960)
    chunk_size: int = 1024             # Audio chunk size in frames
    channels: int = 1                  # Mono audio
    format_width: int = 2              # 16-bit PCM (2 bytes)
    input_device_index: int | None = 1   # WM8960 mic input (hw:1,0)
    output_device_index: int | None = 1  # WM8960 speaker output (hw:1,0)


@dataclass
class GeminiConfig:
    """Configuration for Gemini Live API."""
    model: str = "gemini-2.5-flash-native-audio-preview-12-2025"
    system_instruction: str = "You are a helpful, friendly voice assistant."


@dataclass
class WakeWordConfig:
    """Configuration for wake word detection."""
    enabled: bool = True                  # Enable/disable wake word detection
    model_path: str | None = None         # Path to custom model, None = "hey_jarvis"
    threshold: float = 0.5                # Detection confidence threshold (0.0-1.0)
    timeout: float = 30.0                 # Seconds of silence before returning to listening
    inference_framework: str = "onnx"     # "onnx" or "tflite"
