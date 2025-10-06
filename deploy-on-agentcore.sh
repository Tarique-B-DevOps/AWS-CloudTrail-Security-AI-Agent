#!/bin/bash
set -e

RESOURCE_PREFIX="aws_cloudtrail_agent"
STACK_NAME="${RESOURCE_PREFIX//_/-}"
ENVIRONMENT="prod"
AGENT_VERSION="v1.0.0"
AWS_REGION="us-east-1"
CFN_TEMPLATE="cfn-template.yaml"

REPO_NAME="${RESOURCE_PREFIX}_${ENVIRONMENT}"
WEBAPP_CONTAINER_NAME="${RESOURCE_PREFIX}_webapp"

REQUIRED_ENV_VARS=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION")

check_env_vars() {
  echo "🔹 Checking required environment variables..."
  missing=false
  for var in "${REQUIRED_ENV_VARS[@]}"; do
    if [ -z "${!var}" ]; then
      echo "❌ Environment variable $var is not set."
      missing=true
    fi
  done
  if [ "$missing" = true ]; then
    echo "⚠️  Please set all required environment variables before running the script."
    exit 1
  fi
  echo "✅ All required environment variables are set."
}

delete_resources() {
  echo "🧹 Cleanup mode initiated..."

  if docker ps -a --format '{{.Names}}' | grep -q "^${WEBAPP_CONTAINER_NAME}$"; then
    echo "🔹 Stopping and removing local Streamlit container: $WEBAPP_CONTAINER_NAME"
    docker stop "$WEBAPP_CONTAINER_NAME" >/dev/null || true
    docker rm "$WEBAPP_CONTAINER_NAME" >/dev/null || true
    echo "✅ Local Streamlit container removed."
  else
    echo "⚠️  No local Streamlit container found."
  fi

  echo "🔹 Checking for ECR repository: $REPO_NAME"
  REPO_EXISTS=$(aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" 2>/dev/null || true)

  if [ -z "$REPO_EXISTS" ]; then
    echo "⚠️  ECR repository does not exist. Skipping repository deletion."
  else
    echo "🔹 Deleting all images in repository: $REPO_NAME"
    IMAGE_TAGS=$(aws ecr list-images --repository-name "$REPO_NAME" --region "$AWS_REGION" --query 'imageIds[*]' --output json)
    if [ "$IMAGE_TAGS" != "[]" ]; then
      aws ecr batch-delete-image \
        --repository-name "$REPO_NAME" \
        --image-ids "$IMAGE_TAGS" \
        --region "$AWS_REGION" >/dev/null || true
      echo "✅ Images deleted."
    else
      echo "✅ No images found."
    fi

    echo "🔹 Deleting ECR repository..."
    aws ecr delete-repository --repository-name "$REPO_NAME" --region "$AWS_REGION" --force >/dev/null
    echo "✅ ECR repository deleted."
  fi

  echo "🔹 Deleting CloudFormation stack: $STACK_NAME"
  if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
    aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$AWS_REGION"
    echo "⏳ Waiting for CloudFormation stack to delete..."
    aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$AWS_REGION"
    echo "✅ CloudFormation stack deleted."
  else
    echo "⚠️  No existing CloudFormation stack found."
  fi

  echo "🧩 Cleanup complete."
  exit 0
}

if [[ "$1" == "--delete" ]]; then
  delete_resources
fi

check_env_vars

echo "🔹 Checking or creating ECR repository..."
REPO_EXISTS=$(aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" 2>/dev/null || true)

if [ -z "$REPO_EXISTS" ]; then
  echo "🆕 Repository not found. Creating new ECR repo: $REPO_NAME"
  aws ecr create-repository --repository-name "$REPO_NAME" --region "$AWS_REGION" > /dev/null
else
  echo "✅ Repository already exists: $REPO_NAME"
fi

REPO_URL=$(aws ecr describe-repositories \
  --repository-names "$REPO_NAME" \
  --region "$AWS_REGION" \
  --query "repositories[0].repositoryUri" \
  --output text)

echo "📦 Repository URL: $REPO_URL"

echo "🔹 Authenticating Docker to Amazon ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${REPO_URL%%/*}"

echo "🔹 Building and pushing ARM64 Docker image for the agent..."
docker buildx create --use >/dev/null 2>&1 || true
docker buildx build \
  --platform linux/arm64 \
  -f Dockerfile.agent \
  -t "${REPO_URL}:${AGENT_VERSION}" \
  --push .

echo "✅ Agent Docker image built and pushed: ${REPO_URL}:${AGENT_VERSION}"

echo "🔹 Deploying CloudFormation stack for Bedrock AgentCore runtime..."
aws cloudformation deploy \
  --template-file "$CFN_TEMPLATE" \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --capabilities CAPABILITY_NAMED_IAM

echo "✅ CloudFormation deployment completed."

echo "🔹 Retrieving AgentCore Runtime ARN..."
AGENTCORE_RUNTIME_ARN=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='AgentCoreRuntimeArn'].OutputValue" \
  --output text)

if [ -z "$AGENTCORE_RUNTIME_ARN" ]; then
  echo "❌ ERROR: Unable to retrieve AgentCoreRuntime ARN."
  exit 1
fi

echo "📘 AgentCore Runtime ARN: $AGENTCORE_RUNTIME_ARN"

echo "🔹 Building Streamlit webapp Docker image..."
docker build -t "${RESOURCE_PREFIX}_webapp" -f Dockerfile.webapp .

echo "✅ Streamlit webapp image built successfully."

echo "🚀 Starting Streamlit webapp container..."
if docker ps --format '{{.Names}}' | grep -q "^${WEBAPP_CONTAINER_NAME}$"; then
  echo "🔹 Stopping running container: $WEBAPP_CONTAINER_NAME"
  docker stop "$WEBAPP_CONTAINER_NAME" >/dev/null
fi

if docker ps -a --format '{{.Names}}' | grep -q "^${WEBAPP_CONTAINER_NAME}$"; then
  echo "🔹 Removing existing container: $WEBAPP_CONTAINER_NAME"
  docker rm "$WEBAPP_CONTAINER_NAME" >/dev/null
fi

docker run -d \
  -p 8501:8501 \
  --name "${WEBAPP_CONTAINER_NAME}" \
  -e STRAND_AGENT_RUNTIME="AgentCore" \
  -e STRANDS_AGENTCORE_ARN="${AGENTCORE_RUNTIME_ARN}" \
  -e STRANDS_AGENT_VERSION="${AGENT_VERSION}" \
  -e AWS_REGION="${AWS_REGION}" \
  -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
  -e AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN}" \
  "${RESOURCE_PREFIX}_webapp"

echo ""
echo "✅ Agent is Deployed on AWS Bedrock AgentCore."
echo "🌐 Access the Streamlit app locally at: http://localhost:8501"
echo ""
