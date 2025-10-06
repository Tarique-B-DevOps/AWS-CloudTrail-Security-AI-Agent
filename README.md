# AWS CloudTrail Security Agent

## Overview

**Powered by Strands AI Agent & AWS Bedrock**, the AWS CloudTrail Security Agent provides **intelligent, AI-generated security insights** from your CloudTrail logs using only built-in tools. Key highlights:

* **Strands AI Agent Driven**: Automates querying, summarizing, and highlighting suspicious activity.
* **AWS Bedrock Powered**: Uses cutting-edge models to analyze logs and generate intelligence.
* **Built-In Tools Only**: All tasks are performed without external tools.
* **Deploy on AgentCore**: Experience a fully managed agent runtime by deploying on the latest AWS offering for hosting agentic workloads.
* **Interactive Web Interface**: Chat-style interface for easy query submission and visualization.

Experience a **fast, interactive, and intelligent security assistant** for AWS CloudTrail, generating insights with minimal setup.

<video width="640" height="360" controls>
  <source src="https://github.com/user-attachments/assets/ade274bf-8581-4bec-b08b-2dbe7add8b84" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Click here to watch the video in a new tab](https://github.com/user-attachments/assets/ade274bf-8581-4bec-b08b-2dbe7add8b84)

## Tech Stack

* **Strands AI Agent** for intelligent log analysis and AI-driven automation
* **AWS Bedrock** For generative AI capabilities, the agent leverages Amazon Bedrock as the underlying LLM platform.
* **AWS Bedrock AgentCore** for deployment on agentcore runtime.
* **FastAPI** for API service
* **Docker & Docker Compose** for containerization
* **Streamlit** for interactive web interface

## Features

* Collects and analyzes CloudTrail events within a specified timeframe.
* Highlights suspicious activity and summarizes access patterns.
* Generates AI-powered insights in real-time.
* Chat-style web interface with progress visualization.

## Prerequisites

* **Docker & Docker Compose** installed
* **AWS temporary credentials**
* **AWS Bedrock service enabled** (preferably with **Anthropic model**)

## Running Locally

### Steps

1. Export AWS credentials and Bedrock configuration:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token
export BEDROCK_MODEL_REGION=us-east-1
export BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0
```

*NOTE: replace with your actual values.*

2. Start services with Docker Compose:

```bash
docker compose up --build
```

3. Open the web interface at [http://localhost:8501](http://localhost:8501) and submit queries.

### Example Query

```
analyze the usage pattern of the user tarique in us-east-1 region in last one hour
```

* The agent will stream **real-time AI-generated analysis**, highlighting user activity patterns and any anomalies.


### Deploy on AgentCore

1. Deploy the agent on **AWS Bedrock AgentCore runtime** by running the provided script:

```bash
./deploy-on-agentcore.sh
```

2. Once deployment is complete, access the web UI. The runtime should now be set to **AgentCore**.
3. Submit the same query again; the response will be **generated from the AgentCore runtime**, which is hosting your Strands agent.

> **Use --delete to cleanup**
