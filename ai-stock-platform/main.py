from fastapi import FastAPI
from ai_models import pipeline

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "QuantumVestAI is running"}

@app.get("/predict")
def predict():
    # Placeholder for actual prediction pipeline
    return {"prediction": "This is a mock prediction"}