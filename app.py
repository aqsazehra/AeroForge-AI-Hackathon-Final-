import io
import json
import os
import re
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(page_title="AeroForge AI — Engineering Copilot", page_icon="✈️", layout="wide")

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#F6F9FC,#EDF4FA)}
.block-container{max-width:1500px;padding-top:1rem}
.hero{background:linear-gradient(115deg,#061A31,#0B4D8E,#00A7C7);border-radius:24px;padding:30px 34px;color:white;margin-bottom:18px}
.hero h1{font-size:2.6rem;margin:0 0 8px}.hero p{margin:0 0 6px;opacity:.94}
.badge{display:inline-block;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.14);margin:0 6px 8px 0;font-size:.78rem}
.card{background:white;border:1px solid #E0E8F1;border-radius:18px;padding:18px;box-shadow:0 6px 20px rgba(21,45,73,.06);height:100%}
.metric{background:white;border:1px solid #E0E8F1;border-radius:16px;padding:16px}
.metric .v{font-size:1.7rem;font-weight:750}.metric .l{color:#637083;font-size:.82rem}
.warning{background:#FFF8E7;border-left:4px solid #E7B84B;padding:12px 14px;border-radius:9px}
.success{background:#EAF8F2;border-left:4px solid #1C9B68;padding:12px 14px;border-radius:9px}
.agent{background:white;border:1px solid #DCE6F0;border-radius:14px;padding:13px;margin:8px 0}
</style>
""", unsafe_allow_html=True)

DEFAULT_REQUIREMENTS = """Project: Civil Fixed-Wing UAV Engineering Demonstrator
Mission: Long-endurance mapping / inspection support
MTOW target: 10 kg
Payload target: 2 kg
Wingspan: 3.2 m
Cruise speed target: 80 km/h
Endurance target: 2 hours
Flight controller: CUAV V6X
Telemetry: P9-class telemetry link
Navigation: GNSS + airspeed sensing
Propulsion: electric BLDC motor + ESC + LiPo battery
Structure: carbon/glass composite airframe
Need: requirements review, architecture decisions, starter BOM, manufacturing plan, risk register and verification plan.
Constraint: screening-level engineering only; qualified engineers validate calculations and test decisions."""

AGENTS = [
    ("Requirements Analyst", "Extract measurable requirements, missing units, ambiguities, assumptions and verification methods."),
    ("Systems Engineer", "Create functional architecture, interfaces, budgets and decision gates from the requirements."),
    ("Aerospace Analyst", "Perform screening-level mass, power, propulsion and performance reasoning; state assumptions and margins."),
    ("Manufacturing Engineer", "Translate design intent into BOM fields, composite/CNC process steps, inspection and configuration controls."),
    ("Safety & Test Engineer", "Identify engineering risks, mitigations, verification evidence and staged test gates. Keep recommendations conservative."),
    ("Program Synthesizer", "Combine prior findings into executive decisions, priorities, open actions and measurable impact."),
]

if "requirements" not in st.session_state: st.session_state.requirements = DEFAULT_REQUIREMENTS
if "workflow" not in st.session_state: st.session_state.workflow = {}
if "chat" not in st.session_state: st.session_state.chat = []


def get_secret(name, default=""):
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


def _extract_value(pattern, requirements, default="Not specified"):
    m = re.search(pattern, requirements, re.IGNORECASE)
    return m.group(1) if m else default

def demo_response(agent, requirements, context=""):
    mtow = _extract_value(r"MTOW(?: target)?\s*:\s*([0-9.]+\s*kg)", requirements)
    payload = _extract_value(r"Payload(?: target)?\s*:\s*([0-9.]+\s*kg)", requirements)
    endurance = _extract_value(r"Endurance(?: target)?\s*:\s*([0-9.]+\s*(?:hours?|h))", requirements)
    speed = _extract_value(r"Cruise speed(?: target)?\s*:\s*([0-9.]+\s*km/h)", requirements)
    span = _extract_value(r"Wingspan\s*:\s*([0-9.]+\s*m)", requirements)
    if agent == "Requirements Analyst":
        return f"""### Requirements Intelligence\n- **Baseline extracted:** MTOW {mtow}; payload {payload}; endurance {endurance}; cruise {speed}; wingspan {span}.\n- **Ambiguities to resolve:** operating altitude, wind envelope, temperature, launch/recovery method, reserve policy, payload power/interface, structural load cases.\n- Each requirement should receive an ID, units, tolerance, owner and verification method.\n- **Priority:** safety-critical flight controls, structure, power and communications."""
    if agent == "Systems Engineer":
        return """### Systems Architecture\n- Functional chain: energy storage → power distribution → ESC/motor → propulsion; avionics power → flight controller → GNSS/airspeed/telemetry.\n- Key interfaces: FC↔GNSS, FC↔airspeed, FC↔telemetry, battery↔PDB, ESC↔motor, payload↔airframe.\n- Decision gates: requirements baseline → interface control → mass/power budget → integration review → verification readiness."""
    if agent == "Aerospace Analyst":
        return """### Screening Performance Review\n- Payload fraction = 2/10 = 20%.\n- A 2-hour endurance target requires an explicit energy budget including propulsion efficiency, avionics load, battery usable energy and reserve.\n- Propulsion selection should be validated against aircraft mass, cruise requirement, propeller operating point and thermal limits.\n- Treat all values as preliminary until validated with manufacturer data and flight-test evidence."""
    if agent == "Manufacturing Engineer":
        return """### Manufacturing Plan\n1. Freeze CAD/drawings and configuration revision.\n2. Release composite material/layup schedule and cure process.\n3. Manufacture structural parts with process travelers and inspection points.\n4. CNC-machine interfaces/fixtures where required.\n5. Perform dimensional, visual and NDI checks appropriate to the structure.\n6. Record serial/lot numbers and nonconformances for traceability."""
    if agent == "Safety & Test Engineer":
        return """### Risk & Verification Starter\n| Risk | Priority | Control | Evidence |\n|---|---|---|---|\n| Requirement ambiguity | High | Baseline measurable requirements | Approved requirement set |\n| Power shortfall | High | Worst-case power budget + margin | Bench measurements |\n| CG outside envelope | High | Mass-properties and balance check | Weight/CG record |\n| Telemetry loss | Medium | Interface/range/failsafe checks | Test record |\n| Composite defect | Medium | Process control + inspection/NDI | Inspection report |\n| Integration fault | High | Interface checks + staged ground tests | Test evidence |"""
    return """### Executive Synthesis\n**Decision:** proceed only after requirements, interfaces, mass/power budgets and verification criteria are baselined.\n\n**Top actions:**\n1. Resolve missing operating-envelope and reserve requirements.\n2. Establish mass, CG and power budgets.\n3. Freeze interface definitions and BOM specifications.\n4. Create configuration-controlled verification matrix.\n5. Execute staged bench/ground tests before any flight activity.\n\n**Human gate:** qualified engineers remain final decision authority."""


def ai_call(system_prompt, user_prompt, model=None, max_tokens=1400):
    # Prefer Hugging Face Inference Providers. Keep output bounded so a single
    # engineering report does not consume excessive free-tier credits.
    hf_key = get_secret("HF_TOKEN")
    hf_model = model or get_secret("HF_MODEL", "openai/gpt-oss-20b:fastest")
    if hf_key and OpenAI is not None:
        try:
            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=hf_key,
            )
            result = client.chat.completions.create(
                model=hf_model,
                temperature=0.2,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = result.choices[0].message.content
            return text.strip() if text else None
        except Exception as exc:
            st.warning(f"Hugging Face live AI unavailable; using deterministic engineering fallback. ({type(exc).__name__})")

    # Optional OpenAI fallback if configured later.
    key = get_secret("OPENAI_API_KEY")
    openai_model = model or get_secret("OPENAI_MODEL", "gpt-4.1-mini")
    if not key or OpenAI is None:
        return None
    try:
        client = OpenAI(api_key=key)
        result = client.chat.completions.create(
            model=openai_model,
            temperature=0.2,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = result.choices[0].message.content
        return text.strip() if text else None
    except Exception as exc:
        st.warning(f"Live AI unavailable; using deterministic engineering fallback. ({type(exc).__name__})")
        return None


def verification_matrix_fallback(requirements):
    """Produce a useful matrix even when the live model is unavailable."""
    mtow = _extract_value(r"MTOW(?: target)?\s*:\s*([0-9.]+\s*kg)", requirements)
    payload = _extract_value(r"Payload(?: target)?\s*:\s*([0-9.]+\s*kg)", requirements)
    span = _extract_value(r"Wingspan\s*:\s*([0-9.]+\s*m)", requirements)
    speed = _extract_value(r"Cruise speed(?: target)?\s*:\s*([0-9.]+\s*km/h)", requirements)
    endurance = _extract_value(r"Endurance(?: target)?\s*:\s*([0-9.]+\s*(?:hours?|h))", requirements)
    return f"""### Verification Matrix

| ID | Requirement | Method | Setup / Instrumentation | Acceptance Criterion | Evidence | Status |
|---|---|---|---|---|---|---|
| VR-001 | MTOW target = {mtow} | Inspection + measurement | Calibrated platform scale; configured aircraft | Measured take-off mass meets approved requirement | Weight record | TBD |
| VR-002 | Payload target = {payload} | Measurement | Calibrated scale; representative payload | Payload mass meets approved requirement without exceeding MTOW | Payload record | TBD |
| VR-003 | Wingspan = {span} | Dimensional inspection | Tape/laser measure; approved drawing | Measured span within drawing tolerance | Dimensional inspection report | TBD |
| VR-004 | Cruise speed target = {speed} | Flight/ground instrumentation test | Validated airspeed/GNSS logging; defined test conditions | Demonstrated speed meets approved target under defined conditions | Flight-test data | TBD |
| VR-005 | Endurance target = {endurance} | Controlled endurance test | Flight logger; battery/current/voltage monitoring; defined reserve | Demonstrated endurance meets approved requirement with reserve policy satisfied | Test log | TBD |
| VR-006 | Flight controller and navigation interfaces | Functional test | CUAV FC, GNSS, airspeed sensor, telemetry; ground test setup | Sensors initialize, data is valid, and required interfaces/logging operate correctly | Integration test record | TBD |
| VR-007 | Telemetry link | Range/interface test | Ground station, telemetry radios, logging | Link remains operational throughout approved test envelope and failsafe response is verified | Telemetry test record | TBD |
| VR-008 | Electric propulsion system | Bench test | Motor, ESC, propeller, battery, current/voltage measurement | Current, voltage, temperature and vibration remain within approved limits | Propulsion test report | TBD |
| VR-009 | Composite airframe structure | Inspection + structural verification | Approved drawings/process records; visual/NDI as applicable | No unacceptable defects; structural acceptance criteria satisfied | Inspection/NDI report | TBD |
| VR-010 | Safety/failsafe functions | Functional ground test | Flight controller, telemetry, power and control interfaces | Defined failsafe behaviors operate as approved | Ground-test record | TBD |

**Verification note:** TBD means the project still needs an approved tolerance, test condition, acceptance threshold, responsible owner and configuration-controlled evidence before verification closure.
"""


def run_agent(agent_name, requirements, prior=""):
    role = dict(AGENTS)[agent_name]
    system = f"""You are the {agent_name} in an engineering AI workflow. Role: {role}
Provide concise, technically rigorous decision support for a civil engineering/UAV project. Clearly label assumptions and unknowns. Do not claim certification, airworthiness, flight clearance, or guaranteed performance. Do not provide weaponization, targeting, or harmful payload guidance. Keep calculations screening-level unless supplied with validated data."""
    prompt = f"PROJECT REQUIREMENTS:\n{requirements}\n\nPRIOR AGENT CONTEXT:\n{prior[-10000:]}\n\nReturn a structured engineering review with headings, tables where useful, and actionable next steps."
    live = ai_call(system, prompt)
    return live if live else demo_response(agent_name, requirements, prior)


def run_workflow(requirements):
    outputs = {}
    prior = ""
    progress = st.progress(0, text="Starting six-agent engineering workflow…")
    for i, (name, _) in enumerate(AGENTS, 1):
        progress.progress(int((i / len(AGENTS)) * 100), text=f"Agent {i}/6: {name}")
        outputs[name] = run_agent(name, requirements, prior)
        prior += f"\n\n## {name}\n{outputs[name]}"
    progress.empty()
    return outputs


def extract_text(f):
    if not f:
        return ""
    data = f.getvalue(); name = f.name.lower()
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", "ignore")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
        except Exception as e:
            return f"PDF extraction error: {e}"
    if name.endswith(".docx"):
        try:
            from docx import Document
            return "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
        except Exception as e:
            return f"DOCX extraction error: {e}"
    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data)).to_csv(index=False)
    return ""

with st.sidebar:
    st.markdown("## ✈️ AeroForge AI")
    st.caption("Agentic Engineering Copilot • UAV • Manufacturing • Traceability")
    live = bool(get_secret("HF_TOKEN") or get_secret("OPENAI_API_KEY")) and OpenAI is not None
    st.success("● LIVE AI ENGINE" if live else "● DEMO ENGINE")
    page = st.radio("Navigate", ["Command Center", "AI Engineering Assistant", "Agentic Workflow", "BOM & Procurement", "Risk & Test", "Decision Package", "Impact Dashboard"])
    st.divider()
    if get_secret("HF_TOKEN"):
        st.caption("Live AI: Hugging Face Inference Providers • model: " + get_secret("HF_MODEL", "openai/gpt-oss-20b:fastest"))
    else:
        st.caption("Live AI is enabled through Streamlit Secrets. API keys are never entered into or stored in the browser UI.")

st.markdown("""<div class="hero">
<span class="badge">AGENTIC AI</span><span class="badge">UAV ENGINEERING</span><span class="badge">MANUFACTURING</span><span class="badge">TRACEABILITY</span>
<h1>AeroForge AI</h1>
<p><b>AI Engineering Assistant</b> — transform one engineering requirement set into decisions, BOM actions, manufacturing controls, risks, verification evidence and an executive synthesis.</p>
</div>""", unsafe_allow_html=True)

if page == "Command Center":
    st.header("Engineering Command Center")
    st.write("The hackathon workflow: one requirement set in → six specialist AI roles → traceable engineering outputs.")
    cols = st.columns(4)
    for c, v, l in zip(cols, ["6", "7", "LIVE", "HITL"], ["specialist agents", "workflow modules", "AI engine status", "human-in-the-loop"]):
        c.markdown(f'<div class="metric"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    for col,title,txt in [(a,"🧠 AI Requirement Analysis","Extract requirements, ambiguities, assumptions and verification methods."),(b,"🧾 Engineering Decisions","Translate requirements into architecture, interfaces, performance and procurement decisions."),(c,"🧪 Evidence & Reporting","Generate manufacturing actions, risk controls, verification and executive synthesis.")]:
        col.markdown(f'<div class="card"><h3>{title}</h3><p>{txt}</p></div>', unsafe_allow_html=True)
    st.info("For the 5-minute demo, start with the sample civil UAV requirements and run the complete agentic workflow.")
    if st.button("▶ Run complete hackathon workflow", type="primary", use_container_width=True):
        st.session_state.workflow = run_workflow(st.session_state.requirements)
        st.success("Workflow completed. Open Agentic Workflow to show the six specialist outputs.")

elif page == "AI Engineering Assistant":
    st.header("🧠 AI Engineering Assistant")
    st.write("Paste or upload requirements. The assistant identifies what is known, unknown, assumed and testable.")
    if st.button("Load hackathon demo requirements"):
        st.session_state.requirements = DEFAULT_REQUIREMENTS
        st.session_state.requirements_loaded_from_demo = True
    up = st.file_uploader("Optional: upload requirements PDF/DOCX/TXT/MD/CSV", type=["pdf","docx","txt","md","csv"])
    if up:
        extracted = extract_text(up)
        if extracted:
            st.session_state.requirements = extracted[:24000]
            st.success(f"Loaded {up.name}")
    st.session_state.requirements = st.text_area("Engineering requirements", st.session_state.requirements, height=300)
    action = st.selectbox("AI action", ["Analyze requirements", "Generate engineering decisions", "Generate procurement requirements", "Generate manufacturing plan", "Generate risk and verification plan", "Prepare executive report"])
    if st.button("Run AI Assistant", type="primary"):
        prompts = {
            "Analyze requirements": "Analyze the requirements. Extract measurable requirements, ambiguities, assumptions, missing units/tolerances and verification methods.",
            "Generate engineering decisions": "Turn the requirements into a screening-level system architecture, interfaces, budgets and engineering decision gates.",
            "Generate procurement requirements": "Create a procurement-ready starter BOM specification list. Focus on required specifications, compatibility checks, evidence and acceptance criteria; do not invent supplier claims.",
            "Generate manufacturing plan": "Create a manufacturing and configuration-control plan covering composites, CNC, inspection, travelers, revisions and traceability.",
            "Generate risk and verification plan": "Create a risk register and verification matrix with IDs, methods, evidence, acceptance criteria and status.",
            "Prepare executive report": "Create a concise executive engineering report: objective, key findings, decisions, gaps, risks, verification, next actions and impact."
        }
        system = "You are AeroForge AI, a rigorous engineering decision-support assistant for civil UAV and manufacturing programs. State assumptions, avoid fabricated facts, and keep the human engineer as final authority."
        live_result = ai_call(system, prompts[action] + "\n\nREQUIREMENTS:\n" + st.session_state.requirements)
        st.session_state.workflow["AI Engineering Assistant"] = live_result or demo_response("Requirements Analyst", st.session_state.requirements)
    if "AI Engineering Assistant" in st.session_state.workflow:
        st.markdown(st.session_state.workflow["AI Engineering Assistant"])

elif page == "Agentic Workflow":
    st.header("🤖 Six-Agent Engineering Workflow")
    st.write("This is the centerpiece of the hackathon: specialist roles analyze the same requirement set, pass context forward, and produce a synthesized engineering result.")
    for i,(name,desc) in enumerate(AGENTS,1):
        status = "✓ Complete" if name in st.session_state.workflow else "Ready"
        st.markdown(f'<div class="agent"><b>{i:02d} • {name}</b> — {desc}<br><span class="small">Status: {status}</span></div>', unsafe_allow_html=True)
    if st.button("🚀 Run / refresh six-agent workflow", type="primary"):
        st.session_state.workflow = run_workflow(st.session_state.requirements)
    if st.session_state.workflow:
        tabs = st.tabs([n for n,_ in AGENTS])
        for tab,(name,_) in zip(tabs,AGENTS):
            with tab:
                if name in st.session_state.workflow:
                    st.markdown(st.session_state.workflow[name])
        st.divider()
        st.subheader("Program-level synthesis")
        synth = st.session_state.workflow.get("Program Synthesizer")
        if synth: st.markdown(synth)

elif page == "BOM & Procurement":
    st.header("🧾 BOM & Procurement Intelligence")
    df = pd.DataFrame([
        ["AIR-001","Airframe structure","TBD",1,"Material, layup/core, drawing & revision"],
        ["PROP-001","BLDC motor","TBD",1,"KV, voltage, current, datasheet"],
        ["PROP-002","ESC","TBD",1,"Continuous/peak current, voltage, telemetry"],
        ["PROP-003","Propeller","TBD",1,"Diameter, pitch, material, operating point"],
        ["PWR-001","LiPo battery","TBD",1,"Cells, capacity, C-rating, connector"],
        ["AV-001","Flight controller","CUAV V6X",1,"Interfaces, firmware, logging"],
        ["NAV-001","GNSS","TBD",1,"Constellations, update rate, interface"],
        ["TEL-001","Telemetry","P9-class",1,"Interface, range requirement, configuration"],
        ["SNS-001","Airspeed sensor","TBD",1,"Range, accuracy, interface"]
    ], columns=["ID","Description","Part No.","Qty","Required specification"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info("This is a starter engineering BOM. Final part numbers and supplier suitability must be verified against current datasheets and project configuration.")
    if st.button("Run AI procurement gap analysis", type="primary"):
        result = ai_call(
            "You are a manufacturing/procurement engineering assistant. Review this starter UAV BOM and identify missing specifications, compatibility checks, acceptance criteria and required evidence. Do not invent supplier facts.",
            "STARTER BOM:\n\n" + df.to_markdown(index=False) + "\n\nPROJECT REQUIREMENTS:\n" + st.session_state.requirements,
            max_tokens=1200,
        )
        st.session_state.workflow["BOM Procurement Analysis"] = result or demo_response("Manufacturing Engineer", st.session_state.requirements)
        st.markdown(st.session_state.workflow["BOM Procurement Analysis"])

elif page == "Risk & Test":
    st.header("🧪 Risk, Safety & Verification")
    a,b = st.columns(2)
    if a.button("Generate AI risk register", type="primary"):
        result = run_agent("Safety & Test Engineer", st.session_state.requirements)
        st.session_state.workflow["Safety & Test Engineer"] = result
    if b.button("Generate verification matrix", type="primary"):
        verification_system = """You are AeroForge AI's verification engineer. Create a concise, conservative verification matrix for a civil UAV engineering project. Use only requirements supplied by the user; do not invent compliance claims or supplier facts. Return a Markdown table with exactly these columns: ID, Requirement, Method, Setup / Instrumentation, Acceptance Criterion, Evidence, Status. Use TBD wherever an approved tolerance, threshold, test condition or evidence requirement is not supplied. Keep the matrix practical and suitable for engineering review."""
        result = ai_call(
            verification_system,
            "REQUIREMENTS:\n" + st.session_state.requirements,
            max_tokens=1400,
        )
        st.session_state.workflow["Verification Matrix"] = result or verification_matrix_fallback(st.session_state.requirements)
        st.success("Verification matrix generated. Review all TBD acceptance criteria before using it for formal verification.")
    if "Safety & Test Engineer" in st.session_state.workflow: st.markdown(st.session_state.workflow["Safety & Test Engineer"])
    if "Verification Matrix" in st.session_state.workflow:
        st.divider(); st.markdown(st.session_state.workflow["Verification Matrix"])
    st.markdown('<div class="warning"><b>Safety boundary:</b> AeroForge AI provides engineering documentation and decision support. It does not authorize flight operations, certify an aircraft, or replace qualified engineering, safety or regulatory review.</div>', unsafe_allow_html=True)

elif page == "Decision Package":
    st.header("📋 Engineering Decision Package")
    st.write("Combine the validated outputs from AeroForge into one traceable, executive-ready engineering package.")

    available = {
        "AI Engineering Assistant": "AI Engineering Assistant",
        "Program Synthesizer": "Program Synthesizer",
        "BOM Procurement Analysis": "BOM & Procurement",
        "Safety & Test Engineer": "Risk Register",
        "Verification Matrix": "Verification Matrix",
    }
    missing = [label for key, label in available.items() if key not in st.session_state.workflow]
    if missing:
        st.warning("Some outputs have not been generated yet: " + ", ".join(missing) + ". Generate them first for a complete package.")

    if st.button("🚀 Generate Engineering Decision Package", type="primary", use_container_width=True):
        req = st.session_state.requirements
        sections = []
        sections.append("# AeroForge AI — Engineering Decision Package")
        sections.append(f"**Generated:** {datetime.now().strftime('%d %b %Y %H:%M')}\n\n**Project requirements baseline**\n\n{req}")

        # Use existing agent outputs first; this keeps the package useful even if another live call is unavailable.
        if "AI Engineering Assistant" in st.session_state.workflow:
            sections.append("## 1. AI Requirements Analysis\n\n" + st.session_state.workflow["AI Engineering Assistant"])
        if "Program Synthesizer" in st.session_state.workflow:
            sections.append("## 2. Program-Level Engineering Synthesis\n\n" + st.session_state.workflow["Program Synthesizer"])
        if "BOM Procurement Analysis" in st.session_state.workflow:
            sections.append("## 3. BOM & Procurement Actions\n\n" + st.session_state.workflow["BOM Procurement Analysis"])
        if "Safety & Test Engineer" in st.session_state.workflow:
            sections.append("## 4. Risk Register\n\n" + st.session_state.workflow["Safety & Test Engineer"])
        if "Verification Matrix" in st.session_state.workflow:
            sections.append("## 5. Verification Matrix\n\n" + st.session_state.workflow["Verification Matrix"])

        sections.append("## 6. Engineering Release Gate\n\n- Resolve all TBD requirements, tolerances and acceptance thresholds.\n- Verify component compatibility against current manufacturer datasheets.\n- Baseline mass, CG, power and interface budgets.\n- Review manufacturing process controls and inspection evidence.\n- Complete staged bench/ground verification before flight testing.\n- Qualified engineers remain the final decision authority.")

        package = "\n\n".join(sections)
        system = "You are AeroForge AI's senior engineering program synthesizer. Produce a concise executive decision summary from the supplied engineering package. Do not invent facts. Clearly distinguish requirements, decisions, gaps, risks, verification status and actions. Keep qualified engineers as final authority."
        context = "\n\n".join(sections)
        ai_summary = ai_call(system, "Summarize this package into an executive decision section with: Decision, Key Engineering Findings, Critical Gaps, Top Risks, Verification Readiness, and Next Actions.\n\n" + context, max_tokens=1000)
        if ai_summary:
            package += "\n\n## 7. AI Executive Decision Summary\n\n" + ai_summary

        st.session_state.workflow["Engineering Decision Package"] = package
        st.success("Engineering Decision Package generated.")

    if "Engineering Decision Package" in st.session_state.workflow:
        st.markdown(st.session_state.workflow["Engineering Decision Package"])
        st.download_button(
            "⬇ Download Engineering Decision Package (.md)",
            data=st.session_state.workflow["Engineering Decision Package"],
            file_name="AeroForge_Engineering_Decision_Package.md",
            mime="text/markdown",
            use_container_width=True,
        )

elif page == "Impact Dashboard":
    st.header("📊 Quantified Hackathon Impact")
    st.caption("Use measured timings in the final submission. The defaults below are an illustrative demo scenario.")
    a,b,c = st.columns(3)
    manual = a.number_input("Manual review time (min)", 1, 2000, 120)
    ai_time = b.number_input("AI-assisted time (min)", 1, 2000, 25)
    runs = c.number_input("Comparable runs", 1, 1000, 10)
    reduction = max(0, 1 - ai_time/manual)
    hours = max(0, (manual-ai_time)*runs/60)
    a.metric("Time reduction", f"{reduction*100:.1f}%")
    b.metric("Hours saved", f"{hours:.1f} h")
    c.metric("Runs modeled", runs)
    st.markdown("### Evidence to capture during your real demo")
    st.write("Time-to-output • requirements extracted • ambiguities found • procurement gaps • risks surfaced • verification cases • human corrections • total end-to-end review time.")
    st.success("For the presentation, explicitly label any pre-measured numbers as illustrative. Replace them with your actual timed run before submission.")

st.divider()
st.caption(f"AeroForge AI • Agentic engineering hackathon prototype • {datetime.now().strftime('%d %b %Y')}")
