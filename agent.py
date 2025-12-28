from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, AsyncGenerator
from datetime import datetime, timezone
from strands import Agent
from strands_tools import current_time, use_aws, python_repl
from fastapi.middleware.cors import CORSMiddleware
from strands.models import BedrockModel
import os
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
import os
import json


import logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("strands-agent")
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logging.getLogger("bedrock_agentcore").setLevel(logging.DEBUG)
    logging.getLogger("strands").setLevel(logging.DEBUG)
    logger.info("DEBUG_MODE is enabled. Verbose logging active.")
else:
    logging.getLogger("bedrock_agentcore").setLevel(logging.WARNING)
    logging.getLogger("strands").setLevel(logging.INFO)
    logger.info("Running in production mode (DEBUG_MODE=false).")

BEDROCK_MODEL_REGION = os.getenv("BEDROCK_MODEL_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
AGENTCORE_LTM_MEMORY_ID = os.getenv("AGENTCORE_LTM_MEMORY_ID")
AGENTCORE_LTM_MEMORY_REGION = os.getenv("AGENTCORE_LTM_MEMORY_REGION", "us-east-1")
STRANDS_AGENT_VERSION = os.getenv("AGENT_VERSION", "1.0.0")
STRANDS_AGENT_TITLE = "AWS CloudTrail Security Agent"

bedrock_model = BedrockModel(model_id=BEDROCK_MODEL_ID, region_name=BEDROCK_MODEL_REGION)

system_prompt = """
You are a AWS CloudTrail Security Assistant. Specialize in analyzing AWS CloudTrail logs and reponding in markdown format.

Your responsibilities:
1. Collect AWS CloudTrail events for a specific time period provided by the user.
2. Analyze the events for anomalies or suspicious activities, such as:
   - Unusual API calls
   - Privilege escalation attempts
   - Access from unexpected regions
   - Denied or failed actions
3. Summarize findings clearly by presenting:
   - Common API calls
   - Services accessed
   - Notable or suspicious events
   - Time-based activity patterns (when events occur most frequently)
   - Access patterns (which users/roles/services are accessing resources)
   - Security assessment with explicit flags for suspicious or high-risk activity
4. Ask the user for the required timeframe if not provided.
5. Use AWS tools (`use_aws`) to query CloudTrail data.
6. Use Python tools (`python_repl`) for log analysis (sorting, counting, summarizing, anomaly detection).
7. Respond with concise, actionable security insights. Always highlight suspicious activity explicitly.
8. Use your Long Term Memory to recall previous security incidents, patterns, or user preferences about report formats.

Stay focused on CloudTrail analysis, security insights, and useful summaries. 
Do not provide unrelated information.
"""


# Global cache for in-memory agents (when LTM is disabled)
# Key: session_id, Value: Agent instance
_agent_cache: Dict[str, Agent] = {}

def get_agent(session_id: str, actor_id: str):
    if AGENTCORE_LTM_MEMORY_ID:
        logger.info(f"Initializing agent with LTM Memory ID: {AGENTCORE_LTM_MEMORY_ID}")
        memory_config = AgentCoreMemoryConfig(
            memory_id=AGENTCORE_LTM_MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                "/preferences/{actorId}": RetrievalConfig(top_k=5, relevance_score=0.7),
                "/facts/{actorId}": RetrievalConfig(top_k=10, relevance_score=0.3),
                "/summaries/{actorId}/{sessionId}": RetrievalConfig(top_k=5, relevance_score=0.5)
            }
        )
        
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=memory_config,
            region_name=AGENTCORE_LTM_MEMORY_REGION
        )
        
        return Agent(
            model=bedrock_model,
            tools=[current_time, use_aws, python_repl],
            system_prompt=system_prompt,
            session_manager=session_manager
        )
    else:
        if session_id in _agent_cache:
            logger.info(f"Retrieving cached agent for session: {session_id}")
            return _agent_cache[session_id]

        logger.info(f"Initializing new agent for session: {session_id} (No LTM)")
        new_agent = Agent(
            model=bedrock_model,
            tools=[current_time, use_aws, python_repl],
            system_prompt=system_prompt
        )
        _agent_cache[session_id] = new_agent
        return new_agent

app = FastAPI(title=STRANDS_AGENT_TITLE, version=STRANDS_AGENT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):

    user_message = request.input.get("prompt", "")
    session_id = request.input.get("session_id", f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    actor_id = request.input.get("actor_id", "default_security_analyst")

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="No prompt found in input. Please provide a 'prompt' key in the input."
        )
    
    agent_instance = get_agent(session_id, actor_id)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for event in agent_instance.stream_async(user_message):
                # The event dict may contain "data" key with streamed text chunks
                if "data" in event:
                    # Stream raw text chunks
                    yield event["data"]
            # Optionally, end stream with newline or sentinel text
            yield "\n[END]\n"
        except Exception as e:
            yield f"\n[Error streaming response: {str(e)}]\n"

    return StreamingResponse(event_generator(), media_type="text/plain") # TODO: Use text/event-stream if using SSE on client side

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
