# Audio Forensics for Voice Security

Real-time detection of synthetic (AI-generated) voice using spectrogram-based analysis.

## Features
- Real-time audio analysis
- Spectrogram-based anomaly detection
- Detection within first 10 seconds

## Tech Stack
- Python (ML + DSP)
- PyTorch
- FastAPI
- WebSockets

## Structure
- backend/ → API layer
- ml/ → models + training
- streaming/ → real-time audio ingestion