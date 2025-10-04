from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
from strands import Agent
from strands_tools import current_time, use_aws, python_repl
from strands.models import BedrockModel
import os


BEDROCK_MODEL_REGION = os.getenv("BEDROCK_MODEL_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
AGENT_VERSION = os.getenv("AGENT_VERSION", "1.0.0")
AGENT_TITLE = "CloudTrail Security Agent"

bedrock_model = BedrockModel(model_id=BEDROCK_MODEL_ID, region_name=BEDROCK_MODEL_REGION)


system_prompt = """
You are a CloudTrail Security Assistant.

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
6. Use Python tools (`python`) for log analysis (sorting, counting, summarizing, anomaly detection).
7. Respond with concise, actionable security insights. Always highlight suspicious activity explicitly.

Stay focused on CloudTrail analysis, security insights, and useful summaries. 
Do not provide unrelated information.
"""

strands_agent = Agent(
    model=bedrock_model,
    tools=[current_time, use_aws, python_repl],
    system_prompt=system_prompt
)

app = FastAPI(title=AGENT_TITLE, version=AGENT_VERSION)

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        result = strands_agent(user_message)

        response = {
            "message": result.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": BEDROCK_MODEL_ID,
        }
        return InvocationResponse(output=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
