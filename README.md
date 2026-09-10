# AeroForge AI

**Agentic AI Engineering Copilot for UAV design, manufacturing, procurement, risk, verification, and engineering traceability.**

AeroForge AI transforms a structured engineering requirement set into a connected engineering decision workflow using a live AI model and specialist agent roles.

## What it does

- **AI Engineering Assistant** — extracts measurable requirements, identifies unknowns, assumptions, and engineering considerations.
- **Agentic Workflow** — runs six specialist roles:
  1. Requirements Analyst
  2. Systems Engineer
  3. Aerospace Analyst
  4. Manufacturing Engineer
  5. Safety & Test Engineer
  6. Program Synthesizer
- **BOM & Procurement** — generates a starter engineering BOM and identifies procurement/specification gaps.
- **Risk, Safety & Verification** — generates an AI risk register and verification matrix.
- **Engineering Decision Package** — consolidates requirements, decisions, BOM actions, risks, verification, and open actions.
- **Impact Dashboard** — supports quantified comparison of manual versus AI-assisted engineering workflow time.

## Demonstration scenario

The included demonstration uses a civil fixed-wing UAV engineering scenario for mapping/inspection:

- MTOW target: 10 kg
- Payload target: 2 kg
- Wingspan: 3.2 m
- Cruise speed: 80 km/h
- Endurance: 2 hours

All engineering outputs are screening-level decision support and require qualified engineering review before formal design release, procurement, or flight testing.

## AI architecture

AeroForge AI uses an OpenAI-compatible client with **Hugging Face Inference Providers**. The demonstration configuration uses:

`openai/gpt-oss-20b:fastest`

The application also contains deterministic fallback behavior so the demonstration interface can remain usable when live inference is unavailable.

## Run locally

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create:

`.streamlit/secrets.toml`

with:

```toml
HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN"
HF_MODEL = "openai/gpt-oss-20b:fastest"
```

Never commit `secrets.toml` or `.venv` to GitHub.

Start the application:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Hackathon workflow

**Requirements → AI Analysis → Specialist Agents → BOM/Procurement → Risk → Verification → Decision Package → Impact**

The objective is not to replace engineering judgment. AeroForge AI is designed to reduce repetitive analysis and documentation effort while keeping the engineer in the decision loop.

## Safety and engineering responsibility

This project is intended for benign civil engineering applications such as mapping, inspection, environmental monitoring, research, and manufacturing support. AI-generated recommendations are advisory and must be independently validated by qualified engineers and against current drawings, datasheets, simulations, procedures, and applicable regulations.

## Technology

- Python
- Streamlit
- Hugging Face Inference Providers
- OpenAI-compatible API
- Pandas
- PDF/DOCX/TXT/MD/CSV requirement ingestion

## Project

**AeroForge AI — AI Engineering Copilot**

Built as a prototype for an AI productivity and innovation hackathon.
