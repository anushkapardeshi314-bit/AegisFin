import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import hashlib, json, io

st.set_page_config(page_title="AegisFin", page_icon="🛡️", layout="wide")

DATA = Path(__file__).resolve().parents[1] / "data"
CASES = DATA / "cases.json"

def load_cases():
    if CASES.exists():
        return json.loads(CASES.read_text())
    return []

def save_cases(cases):
    CASES.write_text(json.dumps(cases, indent=2))

def risk_label(score):
    if score < 30: return "LOW"
    if score < 60: return "MEDIUM"
    if score < 80: return "HIGH"
    return "CRITICAL"

def transaction_score(amount, usual_amount, new_beneficiary, new_device, failed_logins, velocity):
    ratio = amount / max(usual_amount, 1)
    score = 0
    score += min(35, max(0, (ratio - 1) * 10))
    score += 20 if new_beneficiary else 0
    score += 15 if new_device else 0
    score += min(15, failed_logins * 5)
    score += min(15, max(0, velocity - 3) * 3)
    return round(min(100, score), 1)

def scam_score(message):
    text = message.lower()
    indicators = {
        "urgency": ["urgent", "immediately", "now", "within 10 minutes", "expire"],
        "financial request": ["payment", "transfer", "upi", "send money", "pay"],
        "credential pressure": ["otp", "pin", "password", "verify account", "verification"],
        "impersonation": ["bank", "police", "customer care", "support", "official"],
        "reward/threat": ["blocked", "prize", "reward", "penalty", "legal action"],
    }
    found = []
    for name, words in indicators.items():
        if any(w in text for w in words):
            found.append(name)
    score = min(100, len(found) * 18 + (12 if "urgency" in found and "financial request" in found else 0))
    return round(score, 1), found

def voice_demo_score(uploaded_file):
    if uploaded_file is None:
        return 0, []
    raw = uploaded_file.getvalue()
    digest = hashlib.sha256(raw).digest()
    # Deterministic demo signal. This is NOT a production deepfake detector.
    score = 45 + digest[0] % 51
    signals = [
        "Audio accepted for privacy-preserving demo analysis",
        "Synthetic-speech indicator score generated from demo feature pipeline",
        "Production deployment should replace this with a validated audio model",
    ]
    return float(score), signals

def fused_score(tx, scam, voice, account=35):
    return round(0.30*tx + 0.25*scam + 0.25*voice + 0.20*account, 1)

st.title("🛡️ AegisFin")
st.caption("AI-assisted financial fraud intelligence prototype • synthetic/demo data only")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Command Center", "Transaction Analyzer", "Voice Analyzer", "Scam Analyzer", "Case Management"])
    st.divider()
    st.info("Prototype only. Do not use this application for real banking decisions, authentication, diagnosis, or payment authorization.")

if page == "Command Center":
    st.subheader("Financial Security Command Center")
    cases = load_cases()
    high = sum(c.get("risk_level") in ["HIGH","CRITICAL"] for c in cases)
    medium = sum(c.get("risk_level") == "MEDIUM" for c in cases)
    resolved = sum(c.get("status") == "Resolved" for c in cases)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Active Cases", len(cases))
    c2.metric("High/Critical", high)
    c3.metric("Medium", medium)
    c4.metric("Resolved", resolved)

    st.divider()
    st.subheader("Detection Pipeline")
    st.code("Voice → Transaction → Scam Pattern → Risk Fusion → Explainability → Review / Report", language="text")

    if cases:
        df = pd.DataFrame(cases)
        st.subheader("Recent Cases")
        show = [c for c in ["id","risk_level","risk_score","status","created_at"] if c in df.columns]
        st.dataframe(df[show].tail(10), use_container_width=True, hide_index=True)
    else:
        st.success("No cases yet. Use the analyzers to create a demo case.")

elif page == "Transaction Analyzer":
    st.subheader("💳 Transaction Risk Analyzer")
    col1,col2 = st.columns(2)
    with col1:
        amount = st.number_input("Transaction amount (₹)", 100.0, 1000000.0, 48500.0, 100.0)
        usual = st.number_input("User's usual transaction amount (₹)", 100.0, 500000.0, 2500.0, 100.0)
        new_ben = st.checkbox("New beneficiary", True)
    with col2:
        new_device = st.checkbox("New device", True)
        failed = st.number_input("Failed login attempts", 0, 10, 3)
        velocity = st.number_input("Transactions in last hour", 0, 20, 6)

    if st.button("Analyze Transaction", type="primary"):
        tx = transaction_score(amount, usual, new_ben, new_device, failed, velocity)
        st.metric("Transaction risk indicator", f"{tx}/100")
        st.progress(int(tx))
        st.write("Risk level:", risk_label(tx))
        reasons = []
        if amount > usual*3: reasons.append("Amount differs substantially from usual behavior.")
        if new_ben: reasons.append("Beneficiary is new.")
        if new_device: reasons.append("Device is new.")
        if failed: reasons.append(f"{failed} failed login attempt(s) observed.")
        if velocity > 3: reasons.append("Transaction velocity is elevated.")
        for r in reasons: st.write("•", r)

elif page == "Voice Analyzer":
    st.subheader("🎙️ Voice Risk Analyzer")
    st.write("Upload a consented/synthetic demonstration audio file. The included detector is a placeholder pipeline for the hackathon UI; replace it with a validated anti-spoofing model before real deployment.")
    audio = st.file_uploader("Upload WAV/MP3/M4A", type=["wav","mp3","m4a"])
    if st.button("Analyze Voice", type="primary"):
        score, signals = voice_demo_score(audio)
        if audio is None:
            st.warning("Upload an audio file first.")
        else:
            st.metric("Synthetic-speech risk indicator", f"{score:.1f}/100")
            st.progress(int(score))
            st.write("Risk level:", risk_label(score))
            for s in signals: st.write("•", s)

elif page == "Scam Analyzer":
    st.subheader("💬 Scam Pattern Analyzer")
    message = st.text_area("Paste a suspicious financial message", height=180,
        value="URGENT: Your bank account will be blocked. Verify your account immediately and send the payment through UPI now.")
    if st.button("Analyze Scam Pattern", type="primary"):
        score, found = scam_score(message)
        st.metric("Scam-pattern risk indicator", f"{score}/100")
        st.progress(int(score))
        st.write("Risk level:", risk_label(score))
        if found:
            st.write("Detected indicators:")
            for x in found: st.write("•", x)
        else:
            st.info("No configured demo indicators detected.")

elif page == "Case Management":
    st.subheader("📁 Case Management")
    cases = load_cases()
    with st.expander("Create integrated demo case", expanded=True):
        c1,c2 = st.columns(2)
        with c1:
            tx = st.slider("Transaction risk", 0, 100, 78)
            scam = st.slider("Scam-pattern risk", 0, 100, 72)
        with c2:
            voice = st.slider("Voice risk", 0, 100, 68)
            account = st.slider("Account anomaly", 0, 100, 55)

        if st.button("Create AegisFin Case", type="primary"):
            overall = fused_score(tx, scam, voice, account)
            case_id = "AF-" + datetime.now().strftime("%Y%m%d%H%M%S")
            case = {
                "id": case_id,
                "risk_score": overall,
                "risk_level": risk_label(overall),
                "status": "Under Review",
                "transaction_risk": tx,
                "scam_risk": scam,
                "voice_risk": voice,
                "account_risk": account,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "recommended_action": "Additional verification and human review before proceeding."
            }
            cases.append(case)
            save_cases(cases)
            st.success(f"Created {case_id} with {case['risk_level']} risk.")
            st.json(case)

    if cases:
        st.divider()
        st.subheader("Cases")
        for c in reversed(cases):
            with st.container(border=True):
                a,b,cx = st.columns([2,1,2])
                a.write(f"**{c['id']}** — {c['risk_level']}")
                b.metric("Risk", c["risk_score"])
                cx.write(c["status"])
                st.caption(c["recommended_action"])
else:
    st.write("Select a module from the sidebar.")
