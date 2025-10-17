# AWS CloudTrail Security AI Agent | Intelligent Log Analysis with Strands AI & AWS Bedrock

[![AWS](https://img.shields.io/badge/AWS-CloudTrail-orange)](https://aws.amazon.com/cloudtrail/)
[![Bedrock](https://img.shields.io/badge/AWS-Bedrock-blue)](https://aws.amazon.com/bedrock/)
[![Strands AI](https://img.shields.io/badge/Strands-AI%20Agent-green)](https://strandsagents.com/latest/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-teal)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-Powered AWS CloudTrail Security Analysis** | Automated threat detection, anomaly detection, and intelligent security insights using Strands AI Agent, AWS Bedrock LLMs, and AgentCore Runtime.

---

## 🎯 Overview

The **AWS CloudTrail Security AI Agent** is an intelligent security monitoring solution that leverages artificial intelligence to analyze AWS CloudTrail logs and detect security threats in real-time. Built on Strands AI Agent framework and powered by AWS Bedrock's advanced language models, this tool provides automated security intelligence without requiring external dependencies.

<video width="640" height="360" controls>
  <source src="https://github.com/user-attachments/assets/ade274bf-8581-4bec-b08b-2dbe7add8b84" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Click here to watch the video in a new tab](https://github.com/user-attachments/assets/ade274bf-8581-4bec-b08b-2dbe7add8b84)

### Key Features

- **🤖 AI-Driven Security Analysis**: Automated CloudTrail log analysis using Strands AI Agent technology
- **☁️ AWS Bedrock Integration**: Leverages Claude 3.5 Sonnet and other Amazon Bedrock LLMs for advanced threat detection
- **🚀 AgentCore Runtime Deployment**: Fully managed agent hosting on AWS Bedrock AgentCore for production workloads
- **🔍 Real-Time Threat Detection**: Identifies suspicious activity, unauthorized access attempts, and anomalous patterns
- **💬 Interactive Chat Interface**: User-friendly Streamlit-based web UI for natural language security queries
- **📊 Intelligent Insights**: Generates human-readable security reports with actionable recommendations
- **🛠️ Zero External Dependencies**: All analysis performed using built-in AWS tools and services
- **🐳 Containerized Deployment**: Easy setup with Docker and Docker Compose

---

## 🏗️ Architecture & Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **AI Agent Framework** | Strands AI Agent | Orchestrates intelligent log analysis and automation |
| **LLM Platform** | AWS Bedrock (Claude 3.5 Sonnet) | Generative AI for security analysis and insights |
| **Runtime Environment** | AWS Bedrock AgentCore | Managed serverless agent hosting |
| **API Layer** | FastAPI | High-performance REST API service |
| **Frontend Interface** | Streamlit | Interactive chat-style web application |
| **Data Source** | AWS CloudTrail | AWS audit and governance log service |
| **Containerization** | Docker & Docker Compose | Simplified deployment and scalability |

### How It Works

1. **Data Collection**: Retrieves CloudTrail events from specified AWS regions and timeframes
2. **AI Processing**: Strands Agent analyzes logs using AWS Bedrock LLMs
3. **Pattern Recognition**: Identifies access patterns, privilege escalations, and anomalies
4. **Intelligence Generation**: Creates natural language security reports with risk assessments
5. **Interactive Delivery**: Streams insights through conversational web interface

---

## 🚀 Quick Start Guide

### Prerequisites

Before installing the AWS CloudTrail Security AI Agent, ensure you have:

- **Docker** (version 20.10+) and **Docker Compose** installed
- **AWS Account** with CloudTrail enabled
- **AWS IAM Credentials** with appropriate permissions:
  - CloudTrail read access (`cloudtrail:LookupEvents`)
  - Bedrock model access (`bedrock:InvokeModel`)
  - AgentCore deployment permissions (optional, for production)
- **AWS Bedrock** service enabled in your region
- **Anthropic Claude 3.5 Sonnet** model access (or compatible Bedrock model)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/Tarique-B-DevOps/AWS-CloudTrail-Security-AI-Agent.git
cd AWS-CloudTrail-Security-AI-Agent
```

#### 2. Configure AWS Credentials

Export your AWS credentials and Bedrock configuration as environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_SESSION_TOKEN=your_session_token  # For temporary credentials
export BEDROCK_MODEL_REGION=us-east-1
export BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

> **Security Note**: Replace placeholder values with your actual AWS credentials. For production, use IAM roles instead of hardcoded credentials.

#### 3. Launch with Docker Compose

Start all services in containerized environment:

```bash
docker compose up --build
```

#### 4. Access the Web Interface

Open your browser and navigate to:

```
http://localhost:8501
```

---

## 📖 Usage Examples

### Security Query Examples

The AI agent understands natural language queries about your CloudTrail logs:

#### Example 1: User Activity Analysis
```
analyze the usage pattern of the user tarique in us-east-1 region in last one hour
```

**Response**: The agent will stream real-time analysis including:
- API calls made by the user
- Resources accessed
- Unusual access patterns
- Potential security risks

#### Example 2: Threat Detection
```
show me any suspicious login attempts in the last 24 hours
```

#### Example 3: Privilege Analysis
```
identify any privilege escalation attempts in the last week
```

#### Example 4: Compliance Audit
```
summarize all IAM policy changes made by admin users today
```

---

## ☁️ Deploying to AWS Bedrock AgentCore Runtime

For production workloads, deploy your AI agent to AWS Bedrock AgentCore for fully managed, serverless hosting:

### Deployment Steps

#### 1. Run the Deployment Script

```bash
./deploy-on-agentcore.sh
```

This script will:
- Package your Strands agent configuration
- Create AgentCore runtime resources
- Deploy the agent to AWS infrastructure
- Configure necessary IAM permissions

#### 2. Verify Deployment

Once deployment completes, access the web UI at `http://localhost:8501`. The runtime indicator should show **AgentCore**.

#### 3. Test Production Agent

Submit the same security queries. Responses will now be generated from the AgentCore runtime, providing:
- **Higher Availability**: Managed AWS infrastructure
- **Better Performance**: Optimized agent execution
- **Auto-Scaling**: Handles variable workloads
- **Cost Efficiency**: Pay only for usage

### Cleanup Resources

To delete AgentCore deployment and associated resources:

```bash
./deploy-on-agentcore.sh --delete
```

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes |
| `AWS_SESSION_TOKEN` | Temporary session token | - | No |
| `BEDROCK_MODEL_REGION` | AWS Bedrock region | `us-east-1` | Yes |
| `BEDROCK_MODEL_ID` | Bedrock model identifier | Claude 3.5 Sonnet | Yes |
| `CLOUDTRAIL_REGION` | CloudTrail region to analyze | `us-east-1` | No |
| `LOG_LEVEL` | Application logging level | `INFO` | No |

### Supported AWS Bedrock Models

- ✅ `us.anthropic.claude-3-5-sonnet-20241022-v2:0` (Recommended)
- ✅ `anthropic.claude-3-sonnet-20240229-v1:0`
- ✅ `anthropic.claude-3-opus-20240229-v1:0`
- ✅ Other Bedrock-supported LLMs

---

## 🎯 Use Cases

### Cloud Security Operations
- **Real-time Threat Monitoring**: Continuous analysis of CloudTrail logs for security events
- **Incident Response**: Quickly investigate suspicious activity with natural language queries
- **Forensic Analysis**: Historical log analysis for post-incident investigations

### Compliance & Auditing
- **Compliance Reporting**: Generate audit reports for SOC 2, ISO 27001, PCI DSS
- **Access Reviews**: Identify and review privileged access patterns
- **Change Tracking**: Monitor infrastructure and configuration changes

### DevSecOps
- **CI/CD Security**: Integrate security checks into deployment pipelines
- **Developer Activity Monitoring**: Track and analyze developer actions in AWS
- **Automated Security Reviews**: Schedule periodic security assessments

---

## 🛡️ Security Best Practices

When deploying the AWS CloudTrail Security AI Agent:

1. **Use IAM Roles**: Prefer IAM roles over access keys for EC2/ECS deployments
2. **Least Privilege**: Grant minimum required permissions for CloudTrail and Bedrock
3. **Encrypt Credentials**: Store sensitive credentials in AWS Secrets Manager or Parameter Store
4. **Network Security**: Deploy in private subnets with appropriate security groups
5. **Audit Logging**: Enable CloudTrail for the agent's own AWS API calls
6. **Regular Updates**: Keep dependencies and Docker images up to date


---

## 🔗 Related Resources

- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands AI Agent Framework](https://strandsagents.com/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
