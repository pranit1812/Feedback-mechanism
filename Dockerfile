FROM python:3.9-slim

WORKDIR /app

# Install curl for health check and AWS CLI for DynamoDB access
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Default environment variables
ENV AWS_REGION=us-east-1
# The following should be passed at runtime or through AWS role
# ENV AWS_ACCESS_KEY_ID=your-access-key
# ENV AWS_SECRET_ACCESS_KEY=your-secret-key

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 