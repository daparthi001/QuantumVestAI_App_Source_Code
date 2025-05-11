# QuantumVestAI

QuantumVestAI is an AI-powered stock prediction platform using ensemble machine learning models and real-time sentiment analysis.

## Features
- FastAPI backend with modular routing
- JWT-based authentication
- Ensemble predictions using Prophet, XGBoost, and LSTM
- Real-time sentiment via NewsAPI and FinBERT
- Retraining pipeline via Kubernetes CronJob
- Deployed with Docker, Terraform, and AWS EKS

## Run Locally
```bash
pip install -r requirements.txt
uvicorn webapi.main:app --reload
```

## Environment Variables (.env)
```
API_KEY=your_newsapi_key
JWT_SECRET=your_jwt_secret
DATABASE_URL=postgresql://admin:pass@host/db
```

## Retrain
```bash
python retrain.py
```