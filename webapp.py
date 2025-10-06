import os
import json
import boto3
import streamlit as st
from streamlit_theme import st_theme
import time
import random
import string

st.set_page_config(page_title="AWS CloudTrail Security Agent", initial_sidebar_state="collapsed")

STRANDS_AGENT_API_BASE = os.getenv("STRANDS_AGENT_API_BASE", "http://localhost:8080")
PING_URL = f"{STRANDS_AGENT_API_BASE}/ping"
API_URL = f"{STRANDS_AGENT_API_BASE}/invocations"

STRAND_AGENT_RUNTIME = os.getenv("STRAND_AGENT_RUNTIME", "Local")  # Options: AgentCore, HTTP
STRANDS_AGENT_VERSION = os.getenv("STRANDS_AGENT_VERSION", "1.0.0")

AGENTCORE_ARN = os.getenv("STRANDS_AGENTCORE_ARN")
AWS_SESSION_ID = ''.join(random.choices(string.ascii_lowercase, k=35))

def check_http_status():
    import requests
    try:
        r = requests.get(PING_URL, timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def check_agentcore_status():
    return bool(AGENTCORE_ARN)

if STRAND_AGENT_RUNTIME == "AgentCore":
    agent_status = check_agentcore_status()
else:
    agent_status = check_http_status()

status_color = "🟢 Connected" if agent_status else "🔴 Disconnected"

st.markdown(
    f"""
    <div style='text-align: center;'>
        <h1>☁️ AWS CloudTrail Security Agent</h1>
        <p style='color: #c5c5c5; font-size: 1.05rem; margin-top: -8px;'>
            Analyze AWS CloudTrail events with security insights.
        </p>
        <p style='font-size: 0.95rem; margin-top: 6px;'>
            <b>Agent Status:</b> {status_color} &nbsp; | &nbsp; <b>Version:</b> {STRANDS_AGENT_VERSION} &nbsp; | &nbsp; <b>Runtime:</b> {STRAND_AGENT_RUNTIME}
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

def invoke_agentcore(prompt: str):
    agent_core_client = boto3.client("bedrock-agentcore", region_name="us-east-1")
    payload = json.dumps({"input": {"prompt": prompt}}).encode("utf-8")

    response_chunks = []

    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    for i in range(0, 95, 5):
        progress_text.text(f"Invoking AgentCore Runtime... {i}%")
        progress_bar.progress(i)
        time.sleep(0.05)

    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=AGENTCORE_ARN,
        runtimeSessionId=AWS_SESSION_ID,
        payload=payload,
    )

    content_type = response.get("contentType", "")
    stream = response.get("response")

    if "text/event-stream" in content_type:
        for line in stream.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data = decoded[6:]
                response_chunks.append(data)

    elif content_type == "application/json":
        body = stream.read()
        if body:
            response_chunks.append(body.decode("utf-8"))

    else:
        chunk_size = 128
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            response_chunks.append(chunk.decode("utf-8"))

    progress_text.text("Invoking AgentCore Runtime... 100% ✅")
    progress_bar.progress(100)
    time.sleep(0.1)
    progress_text.empty()
    progress_bar.empty()

    return "".join(response_chunks)


def invoke_http(prompt: str, response_container):
    import requests
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
                    full_text = "".join(response_chunks)
                    response_container.markdown(full_text, unsafe_allow_html=False)
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

    return "".join(response_chunks)


if prompt := st.chat_input("Type your analysis query and press Enter..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=False)

    with st.chat_message("assistant"):
        response_container = st.empty()
        response_chunks = []

        if STRAND_AGENT_RUNTIME == "AgentCore":
            response_text = invoke_agentcore(prompt)
            response_chunks.append(response_text)
            response_container.markdown("".join(response_chunks), unsafe_allow_html=False)
        else:
            response_text = invoke_http(prompt, response_container)
            response_chunks.append(response_text)

        full_response = clean_markdown("".join(response_chunks))
        st.session_state.messages.append({"role": "assistant", "content": full_response})


theme = st_theme() or {}
theme_base = theme.get("base", "dark")
is_light_mode = theme_base == "light"

if is_light_mode:
    st.markdown(
        """
        <style>
        .block-container { max-width: 880px; margin: 0 auto; }
        .stChatMessage { width: 100%; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px !important; line-height: 1.55; box-shadow: 0 1px 4px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
        .stChatMessage:has(.stMarkdown) { background-color: #f9f9f9 !important; color: #111111 !important; }
        [data-testid="stChatMessage"]:has(.stMarkdown):last-child { background-color: #e9e9e9 !important; color: #111111 !important; align-items: flex-start !important; text-align: left !important; }
        code, pre { background-color: #f1f1f1 !important; color: #222222 !important; font-family: 'Source Code Pro', monospace; font-size: 0.9rem; border-radius: 6px; padding: 6px; }
        .stChatInput { max-width: 880px; margin: 0 auto; }
        .stChatInput input { background: #ffffff !important; color: #111111 !important; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .block-container { max-width: 880px; margin: 0 auto; }
        .stChatMessage { width: 100%; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px !important; line-height: 1.55; box-shadow: 0 1px 4px rgba(0,0,0,0.4); display: flex; flex-direction: column; }
        .stChatMessage:has(.stMarkdown) { background-color: #141414 !important; color: #e2e2e2 !important; }
        [data-testid="stChatMessage"]:has(.stMarkdown):last-child { background-color: #1b1b1b !important; color: #e2e2e2 !important; align-items: flex-start !important; text-align: left !important; }
        code, pre { background-color: #232336 !important; color: #d4d4d4 !important; font-family: 'Source Code Pro', monospace; font-size: 0.9rem; border-radius: 6px; padding: 6px; }
        .stChatInput { max-width: 880px; margin: 0 auto; }
        .stChatInput input { background: #232336 !important; color: #e2e2e2 !important; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
