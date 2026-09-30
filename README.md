# AegisFin 🛡️

AegisFin is an AI-assisted financial fraud intelligence prototype combining:

- Transaction anomaly scoring
- Scam-pattern recognition
- Voice-risk analysis demo pipeline
- Multi-signal risk fusion
- Explainable indicators
- Case management

## Run locally

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
streamlit run app/main.py
```

## Important

This repository is a hackathon prototype using synthetic/demo data. The voice analyzer intentionally uses a deterministic placeholder signal rather than claiming to provide a production-grade deepfake detector. For real deployment, replace it with a validated anti-spoofing/synthetic-speech model, add secure authentication, encryption, proper model evaluation, monitoring, and institution-specific compliance controls.

## Architecture

Voice / Transaction / Message
        ↓
Feature extraction
        ↓
Individual risk indicators
        ↓
Risk fusion
        ↓
Explainability
        ↓
Human review / verification / reporting
