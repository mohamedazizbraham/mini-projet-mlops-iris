import numpy as np
import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.data import split
from src.train import model_for

SAMPLE = dict(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2)


def test_split_disjoint_and_stratified():
    x_train, x_test, y_train, y_test = split()
    assert len(x_train) == 120 and len(x_test) == 30
    assert not set(x_train.index) & set(x_test.index)
    assert y_train.value_counts().tolist() == [40, 40, 40]
    assert y_test.value_counts().tolist() == [10, 10, 10]


def test_reproducibility():
    x, _, y, _ = split()
    a, b = model_for('logistic', 1.0), model_for('logistic', 1.0)
    assert np.array_equal(a.fit(x, y).predict(x), b.fit(x, y).predict(x))


@pytest.mark.parametrize('version', ['v1', 'v2'])
def test_release_contract(monkeypatch, version):
    monkeypatch.setenv('MODEL_VERSION', version)
    with TestClient(app) as client:
        response = client.post('/predict', json=SAMPLE)
        assert response.status_code == 200
        assert response.json()['species'] == 'setosa'
        assert response.json()['model_version'] == version
        assert client.get('/health').json()['status'] == 'ok'
        assert client.post('/predict', json={**SAMPLE, 'petal_width': -1}).status_code == 422
        assert client.post('/predict', json={}).status_code == 422
        assert client.post('/predict', json={**SAMPLE, 'surprise': 1}).status_code == 422
        assert client.get('/metrics').json()['errors'] == 3
