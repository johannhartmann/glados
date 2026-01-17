.PHONY: help install run test clean devices lint format

# Default target
help:
	@echo "Voice Assistant - Makefile Commands"
	@echo ""
	@echo "  make install    Install dependencies with uv"
	@echo "  make run        Run the voice assistant"
	@echo "  make test       Run validation tests"
	@echo "  make devices    List available audio devices"
	@echo "  make clean      Remove build artifacts and cache"
	@echo "  make lint       Run type checking with mypy"
	@echo "  make format     Format code with ruff"
	@echo ""

# Install dependencies
install:
	uv sync

# Run the voice assistant
run:
	uv run voice-assistant

# Run tests
test:
	uv run python tests/test_voice_assistant.py

# List audio devices
devices:
	@uv run python -c "\
import pyaudio; \
pa = pyaudio.PyAudio(); \
print('Available Audio Devices:'); \
print('-' * 60); \
[print(f'[{i}] {pa.get_device_info_by_index(i)[\"name\"]:40} In:{pa.get_device_info_by_index(i)[\"maxInputChannels\"]} Out:{pa.get_device_info_by_index(i)[\"maxOutputChannels\"]}') for i in range(pa.get_device_count())]; \
pa.terminate()" 2>/dev/null

# Test microphone (records 3 seconds)
test-mic:
	@echo "Testing microphone for 3 seconds..."
	@uv run python -c "\
import asyncio; \
from voice_assistant.audio import AudioCapture; \
from voice_assistant.config import AudioConfig; \
async def test(): \
    config = AudioConfig(); \
    capture = AudioCapture(config); \
    capture.start(); \
    count = 0; \
    async for chunk in capture.stream(): \
        count += 1; \
        print(f'Chunk {count}: {len(chunk)} bytes'); \
        if count >= 50: break; \
    capture.stop(); \
asyncio.run(test())" 2>/dev/null

# Test speaker (plays 440Hz tone)
test-speaker:
	@echo "Playing 440Hz test tone..."
	@uv run python -c "\
import math, struct; \
from voice_assistant.audio import AudioPlayer; \
from voice_assistant.config import AudioConfig; \
config = AudioConfig(); \
player = AudioPlayer(config); \
player.start(); \
samples = [struct.pack('<h', int(16000 * math.sin(2 * math.pi * 440 * i / 16000))) for i in range(16000)]; \
player.play_sync(b''.join(samples)); \
player.stop(); \
print('Done')" 2>/dev/null

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf __pycache__/
	rm -rf src/**/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Lint with mypy (install first: uv add --dev mypy)
lint:
	uv run mypy src/voice_assistant/

# Format with ruff (install first: uv add --dev ruff)
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/
