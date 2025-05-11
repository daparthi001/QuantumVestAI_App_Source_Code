# QuantumVestAI

QuantumVestAI is a multi-modal AI platform for predicting stock volatility using time series, sentiment, and visual features. It includes a Dockerized FastAPI backend, machine learning models, CI/CD automation, and infrastructure-as-code with Terraform for AWS deployment.

---

## 🧱 Project Structure

```
ai-stock-platform/
├── ai_models/          # ML models (BERT, LSTM, Prophet, etc.)
├── webapi/             # FastAPI route handlers
├── main.py             # FastAPI app entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker build script
├── .env                # Environment variables

ci-cd/
├── .github/workflows/  # GitHub Actions CI/CD
├── k8s/                # Kubernetes manifests

terraform/              # AWS infrastructure (EKS, VPC, RDS, ECR, etc.)
tests/                  # Unit & integration tests
README.md               # This file
```

---

## 🚀 Deployment Instructions

### 1. Set Up Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### 2. Docker Build (Manually)
```bash
cd ai-stock-platform
docker build -t quantumvestai .
docker run -p 8000:8000 --env-file .env quantumvestai
```

### 3. CI/CD Automation (GitHub Actions)

#### Secrets Required:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Push to `main` branch triggers:
- Terraform provisioning
- Docker build & push to ECR
- Kubernetes deployment to EKS

---

## 🔗 URLs & Access

- **Service**: LoadBalancer IP or Route53 DNS
- **API Test**: `http://<ALB-DNS>/docs`
- **CronJob**: Retrains model daily via Kubernetes CronJob

---

## 📦 Features

- 📈 Prophet + LSTM for price trends
- 📰 FinBERT for financial sentiment
- 🖼️ CLIP/ViT for chart-based insights
- ⚙️ End-to-end deployable on AWS (EKS + ECR)