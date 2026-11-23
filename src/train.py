"""ZenML orchestration, MLflow tracking and Optuna selection on training CV only."""
import json
import os
import subprocess
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import mlflow
import optuna
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, ConfusionMatrixDisplay
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from zenml import pipeline, step
from zenml.client import Client
from src.data import CLASSES, fingerprint, split


def model_for(kind, c):
    classifier = (LogisticRegression(C=c, max_iter=1000, random_state=42)
                  if kind == 'logistic' else SVC(C=c, kernel='rbf', probability=True, random_state=42))
    return make_pipeline(StandardScaler(), classifier)


def revision():
    result = subprocess.run(['git', '-c', 'safe.directory=/app', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip() or 'uncommitted'


@step
def data_step() -> str:
    split()  # validate the versioned input before training
    return fingerprint()


@step
def train_step(data_hash: str, name: str, kind: str, c: float) -> dict:
    x_train, _, y_train, _ = split()
    estimator = model_for(kind, c)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv = cross_val_score(estimator, x_train, y_train, scoring='f1_macro', cv=folds)
    estimator.fit(x_train, y_train)
    path = Path('models') / f'{name}.joblib'
    path.parent.mkdir(exist_ok=True)
    joblib.dump(estimator, path)
    return dict(name=name, kind=kind, C=c, data_sha256=data_hash,
                cv_f1_macro=float(cv.mean()), cv_std=float(cv.std()), model_path=str(path))


@step
def eval_step(result: dict) -> dict:
    # Holdout is evaluated only for releases, after all model selection is complete.
    if result['name'] in ('v1', 'v2'):
        _, x_test, _, y_test = split()
        pred = joblib.load(result['model_path']).predict(x_test)
        result['test_accuracy'] = float(accuracy_score(y_test, pred))
        result['test_f1_macro'] = float(f1_score(y_test, pred, average='macro'))
        ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=CLASSES)
        plt.tight_layout()
        Path('reports').mkdir(exist_ok=True)
        plt.savefig(f"reports/confusion_{result['name']}.png", dpi=150)
        plt.close()
    return result


@step
def export_step(result: dict) -> str:
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///runtime/mlflow.db'))
    mlflow.set_experiment('Iris-MLOps')
    with mlflow.start_run(run_name=result['name']) as run:
        mlflow.log_params({k: result[k] for k in ['kind', 'C', 'data_sha256']})
        mlflow.log_params(dict(seed=42, cv_folds=5, train_rows=120, test_rows=30))
        mlflow.set_tags({'git_commit': revision(), 'pipeline': 'iris_pipeline'})
        mlflow.log_metrics({k: result[k] for k in ['cv_f1_macro', 'cv_std', 'test_accuracy', 'test_f1_macro'] if k in result})
        mlflow.log_artifact(result['model_path'], 'model')
        if result['name'] in ('v1', 'v2'):
            mlflow.log_artifact(f"reports/confusion_{result['name']}.png", 'figures')
        result['mlflow_run_id'] = run.info.run_id
        result['git_commit'] = revision()
        metadata = Path('models') / f"{result['name']}.json"
        metadata.write_text(json.dumps(result, indent=2), encoding='utf-8')
        mlflow.log_artifact(str(metadata), 'model')
    return str(metadata)


@pipeline(enable_cache=False)
def iris_pipeline(name: str, kind: str, c: float):
    data_hash = data_step()
    fitted = train_step(data_hash, name, kind, c)
    evaluated = eval_step(fitted)
    export_step(evaluated)


def main():
    Path('runtime').mkdir(exist_ok=True)
    Path('reports').mkdir(exist_ok=True)
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///runtime/mlflow.db'))
    mlflow.set_experiment('Iris-MLOps')
    x_train, _, y_train, _ = split()
    folds = StratifiedKFold(5, shuffle=True, random_state=42)
    def objective(trial):
        kind = trial.suggest_categorical('kind', ['logistic', 'svm'])
        c = trial.suggest_float('C', 0.05, 50, log=True)
        scores = cross_val_score(model_for(kind, c), x_train, y_train, cv=folds, scoring='f1_macro')
        with mlflow.start_run(run_name=f'optuna-{trial.number:02d}'):
            mlflow.log_params(trial.params)
            mlflow.log_params(dict(seed=42, cv_folds=5, data_sha256=fingerprint()))
            mlflow.log_metric('cv_f1_macro', float(scores.mean()))
            mlflow.set_tag('git_commit', revision())
        return float(scores.mean())
    study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=42, n_startup_trials=3))
    study.optimize(objective, n_trials=8)
    study.trials_dataframe().to_csv('reports/optuna_trials.csv', index=False)
    best = study.best_params
    configs = [('v1', 'logistic', 1.0), ('variation-low-C', 'logistic', 0.1),
               ('variation-svm', 'svm', 1.0), ('v2', best['kind'], best['C'])]
    for name, kind, c in configs:
        iris_pipeline(name=name, kind=kind, c=float(c))
    results = [json.loads(Path(f'models/{name}.json').read_text()) for name, _, _ in configs]
    Path('reports/comparison.json').write_text(json.dumps(results, indent=2))
    runs = Client().list_pipeline_runs(size=20)
    evidence = [{'id':str(r.id), 'name':r.name, 'status':str(r.status)} for r in runs.items]
    Path('reports/zenml_runs.json').write_text(json.dumps(evidence, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
