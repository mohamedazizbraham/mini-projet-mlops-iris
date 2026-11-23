"""Public Iris dataset bundled with scikit-learn; no network download."""
import hashlib
from pathlib import Path
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

FEATURES = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
CLASSES = ['setosa', 'versicolor', 'virginica']
DATA = Path('data/iris.csv')


def prepare():
    iris = load_iris()
    frame = pd.DataFrame(iris.data, columns=FEATURES)
    frame['target'] = iris.target
    DATA.parent.mkdir(exist_ok=True)
    frame.to_csv(DATA, index=False, lineterminator='\n')
    return fingerprint()


def fingerprint():
    return hashlib.sha256(DATA.read_bytes()).hexdigest()


def split():
    frame = pd.read_csv(DATA)
    if list(frame.columns) != FEATURES + ['target'] or frame.isna().any().any():
        raise ValueError('Invalid dataset schema or missing values')
    return train_test_split(frame[FEATURES], frame.target, test_size=0.2,
                            random_state=42, stratify=frame.target)


if __name__ == '__main__':
    print(prepare())
