AeroForge AI — Hugging Face free-tier patch

Replace the app.py in your existing AeroForge_AI_Hackathon_Upgrade_FINAL project with this app.py.

Then create:
.streamlit\secrets.toml

with:
HF_TOKEN = "PASTE_YOUR_HUGGING_FACE_TOKEN_HERE"
HF_MODEL = "openai/gpt-oss-20b:fastest"

Never commit secrets.toml to GitHub.
