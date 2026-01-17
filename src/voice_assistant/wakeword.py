"""Wake word detection using openWakeWord."""

import numpy as np
import openwakeword
from openwakeword.model import Model


class WakeWordDetector:
    """Local wake word detection using openWakeWord.

    openWakeWord processes audio in 80ms chunks (1280 samples at 16kHz).
    Smaller chunks are buffered until enough data is available.
    """

    def __init__(
        self,
        model_path: str | None = None,
        threshold: float = 0.5,
        inference_framework: str = "onnx",
    ):
        """Initialize the wake word detector.

        Args:
            model_path: Path to custom .onnx model, or None to use "hey_jarvis".
            threshold: Detection confidence threshold (0.0 to 1.0).
            inference_framework: Inference backend ("onnx" or "tflite").
        """
        # Download default models if needed
        openwakeword.utils.download_models()

        # Load the model
        if model_path:
            self.model = Model(
                wakeword_models=[model_path],
                inference_framework=inference_framework,
            )
            self._model_names = [model_path.split("/")[-1].replace(".onnx", "")]
        else:
            self.model = Model(
                wakeword_models=["hey_jarvis"],
                inference_framework=inference_framework,
            )
            self._model_names = ["hey_jarvis"]

        self.threshold = threshold
        self._buffer = np.array([], dtype=np.int16)

        # openWakeWord expects 80ms frames (1280 samples at 16kHz)
        self._chunk_samples = 1280

    def process_audio(self, audio_chunk: bytes) -> str | None:
        """Process 16kHz 16-bit PCM audio and detect wake words.

        Args:
            audio_chunk: Raw PCM audio bytes (16-bit, 16kHz, mono).

        Returns:
            Name of detected wake word, or None if no detection.
        """
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_chunk, dtype=np.int16)

        # Append to buffer
        self._buffer = np.concatenate([self._buffer, audio_array])

        # Process complete 80ms chunks
        while len(self._buffer) >= self._chunk_samples:
            chunk = self._buffer[: self._chunk_samples]
            self._buffer = self._buffer[self._chunk_samples :]

            # Get prediction scores
            prediction = self.model.predict(chunk)

            # Check each wake word against threshold
            for wake_word, score in prediction.items():
                if score >= self.threshold:
                    self.reset()
                    return wake_word

        return None

    def reset(self) -> None:
        """Reset detection state and clear buffer."""
        self.model.reset()
        self._buffer = np.array([], dtype=np.int16)

    @property
    def model_names(self) -> list[str]:
        """Return list of loaded wake word model names."""
        return self._model_names
