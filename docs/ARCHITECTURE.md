# QuantumVestAI Architecture

The diagram below illustrates the major components of the application and how they interact. It shows the flow from the user interface through the API to the database and machine learning models.

```mermaid
graph TD
    user((User))
    ui["UI (FastAPI & Jinja2)"]
    api["API Service (FastAPI)"]
    db[(PostgreSQL Database)]
    model_manager["Model Manager"]
    lstm[LSTM Models]
    ensemble[Ensemble Predictor]
    s3[(AWS S3 Model Storage)]

    user --> ui
    ui --> api
    api --> db
    api --> model_manager
    model_manager --> lstm
    model_manager --> ensemble
    lstm <--> s3
```

The UI uses FastAPI and Jinja2 templates to render pages. The API service exposes REST endpoints for authentication, portfolio management, and prediction requests. Machine learning models (primarily LSTM-based) are managed by the `ModelManager` class, which can load models from local storage or AWS S3 and is capable of combining them using an ensemble predictor. The API persists data in a PostgreSQL database.

An optional `ChatGPTService` allows the UI to send questions to OpenAI's ChatGPT API. When enabled, this service provides conversational explanations about predictions and market trends directly in the interface.
