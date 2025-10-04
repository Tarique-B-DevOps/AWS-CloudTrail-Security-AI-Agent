import os
import streamlit as st
import requests
from streamlit_theme import st_theme

st.set_page_config(page_title="AWS CloudTrail Security Agent", initial_sidebar_state="collapsed")

STRANDS_AGENT_API_BASE = os.getenv("STRANDS_AGENT_API_BASE", "http://localhost:8888")
PING_URL = f"{STRANDS_AGENT_API_BASE}/ping"
API_URL = f"{STRANDS_AGENT_API_BASE}/invocations"

def check_agent_status():
    try:
        r = requests.get(PING_URL, timeout=3)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    return False

agent_status = check_agent_status()
agent_version = os.getenv("STRANDS_AGENT_VERSION", "1.0.0")
agent_runtime = os.getenv("STRAND_AGENT_RUNTIME", "Local")

status_color = "🟢 Connected" if agent_status else "🔴 Disconnected"

st.markdown(
    f"""
    <div style='text-align: center;'>
        <h1>☁️ AWS CloudTrail Security Agent</h1>
        <p style='color: #c5c5c5; font-size: 1.05rem; margin-top: -8px;'>
            Analyze AWS CloudTrail events with security insights.
        </p>
        <p style='font-size: 0.95rem; margin-top: 6px;'>
            <b>Agent Status:</b> {status_color} &nbsp; | &nbsp; <b>Version:</b> {agent_version} &nbsp; | &nbsp; <b>Runtime:</b> {agent_runtime}
        </p>
    </div>
    <hr style='margin-top: 10px; margin-bottom: 15px;'>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

def clean_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").strip()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=False)

if prompt := st.chat_input("Type your analysis query and press Enter..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=False)

    with st.chat_message("assistant"):
        response_container = st.empty()
        response_chunks = []
        prev_text = ""

        try:
            with requests.post(
                API_URL,
                json={"input": {"prompt": prompt}},
                stream=True,
                timeout=180,
            ) as resp:
                for chunk in resp.iter_content(chunk_size=128):
                    if not chunk:
                        continue
                    decoded = chunk.decode("utf-8")
                    if "[END]" in decoded:
                        decoded = decoded.replace("[END]", "")
                        response_chunks.append(decoded)
                        break
                    decoded_clean = decoded.replace("[END]", "")
                    if decoded_clean.startswith(prev_text):
                        new_text = decoded_clean[len(prev_text):]
                    else:
                        new_text = decoded_clean
                    prev_text = decoded_clean
                    if new_text.strip():
                        response_chunks.append(new_text)
                        full_text = "".join(response_chunks)
                        response_container.markdown(full_text, unsafe_allow_html=False)
        except Exception as e:
            response_container.markdown(f"**Error:** {e}")

        full_response = clean_markdown("".join(response_chunks))
        st.session_state.messages.append({"role": "assistant", "content": full_response})


theme = st_theme() or {}
theme_base = theme.get("base", "dark")
is_light_mode = (theme_base == "light")

if is_light_mode:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 880px;
            margin: 0 auto;
        }
        .stChatMessage {
            width: 100%;
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px !important;
            line-height: 1.55;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        /* Assistant cards */
        .stChatMessage:has(.stMarkdown) {
            background-color: #f9f9f9 !important;
            color: #111111 !important;
        }
        /* User cards */
        [data-testid="stChatMessage"]:has(.stMarkdown):last-child {
            background-color: #e9e9e9 !important;
            color: #111111 !important;
            align-items: flex-start !important;
            text-align: left !important;
        }
        code, pre {
            background-color: #f1f1f1 !important;
            color: #222222 !important;
            font-family: 'Source Code Pro', monospace;
            font-size: 0.9rem;
            border-radius: 6px;
            padding: 6px;
        }
        .stChatInput {
            max-width: 880px;
            margin: 0 auto;
        }
        .stChatInput input {
            background: #ffffff !important;
            color: #111111 !important;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 880px;
            margin: 0 auto;
        }
        .stChatMessage {
            width: 100%;
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px !important;
            line-height: 1.55;
            box-shadow: 0 1px 4px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
        }
        /* Assistant cards */
        .stChatMessage:has(.stMarkdown) {
            background-color: #141414 !important;
            color: #e2e2e2 !important;
        }
        /* User cards */
        [data-testid="stChatMessage"]:has(.stMarkdown):last-child {
            background-color: #1b1b1b !important;
            color: #e2e2e2 !important;
            align-items: flex-start !important;
            text-align: left !important;
        }
        code, pre {
            background-color: #232336 !important;
            color: #d4d4d4 !important;
            font-family: 'Source Code Pro', monospace;
            font-size: 0.9rem;
            border-radius: 6px;
            padding: 6px;
        }
        .stChatInput {
            max-width: 880px;
            margin: 0 auto;
        }
        .stChatInput input {
            background: #232336 !important;
            color: #e2e2e2 !important;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
