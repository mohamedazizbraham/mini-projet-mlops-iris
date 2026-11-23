"""Stable serving contract. Release selected on process startup, rollback by Compose."""
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from src.data import CLASSES, FEATURES


class Flower(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    sepal_length: float = Field(gt=0, le=20)
    sepal_width: float = Field(gt=0, le=20)
    petal_length: float = Field(gt=0, le=20)
    petal_width: float = Field(gt=0, le=20)


@asynccontextmanager
async def lifespan(app):
    version = os.getenv('MODEL_VERSION', 'v1')
    if version not in ('v1', 'v2'):
        raise ValueError('MODEL_VERSION must be v1 or v2')
    app.state.model = joblib.load(f'models/{version}.joblib')
    app.state.metadata = json.loads(Path(f'models/{version}.json').read_text())
    app.state.version = version
    app.state.requests = 0
    app.state.errors = 0
    app.state.total_ms = 0.0
    yield


app = FastAPI(title='Iris MLOps', version='1.0', lifespan=lifespan)


@app.middleware('http')
async def monitor(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    if request.url.path == '/predict':
        app.state.requests += 1
        app.state.errors += int(response.status_code >= 400)
        app.state.total_ms += (time.perf_counter()-start)*1000
    return response


@app.get('/health')
def health():
    return {'status': 'ok', 'model_version': app.state.version,
            'mlflow_run_id': app.state.metadata['mlflow_run_id']}


@app.post('/predict')
def predict(flower: Flower):
    x = pd.DataFrame([flower.model_dump()], columns=FEATURES)
    prediction = int(app.state.model.predict(x)[0])
    return {'species': CLASSES[prediction], 'class_id': prediction,
            'model_version': app.state.version, 'mlflow_run_id': app.state.metadata['mlflow_run_id']}


@app.get('/metrics')
def metrics():
    n = app.state.requests
    return {'predict_requests': n, 'errors': app.state.errors,
            'mean_latency_ms': app.state.total_ms / n if n else 0}
