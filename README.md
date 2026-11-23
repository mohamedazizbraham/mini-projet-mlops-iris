# Iris MLOps : entraînement traçable, déploiement et rollback

Mini-projet CPU pour une présentation de 5 à 10 minutes, avec une démo de 2 minutes environ. Le modèle prédit l'une des trois espèces d'Iris à partir de quatre mesures en centimètres.

## Démarrage Windows

Prérequis : Docker Desktop démarré (conteneurs Linux), Git et PowerShell. Aucun Python local nécessaire. Ouvrir PowerShell dans ce dossier.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```

La première construction télécharge les dépendances et prend plusieurs minutes. Le script prépare les données, prouve le push/pull DVC dans un espace vierge, entraîne les modèles, lance les tests et démarre l'API. À faire AVANT l'oral.

Une fois préparé :

```powershell
docker compose up -d --wait mlflow api
powershell -ExecutionPolicy Bypass -File scripts/demo.ps1
```

Appuyer sur Entrée trois fois : v1, v2, rollback v1. Le script vérifie automatiquement la version et la prédiction. Pour une exécution sans pauses, ajouter `-Auto`. Les résultats sont conservés dans `evidence/deployment.json`. Le retour à v1 doit retrouver le même identifiant MLflow qu'au départ.

- API et formulaire d'essai : http://localhost:8500/docs
- Suivi MLflow : http://localhost:5500
- État du service : http://localhost:8500/health
- Monitoring minimal : http://localhost:8500/metrics

## Protocole scientifique

Dataset public Iris fourni par scikit-learn : 150 observations, 4 mesures, 3 classes équilibrées. Split stratifié fixe : 120 lignes d'entraînement et 30 lignes de test, graine 42. Le scaler est inclus dans un pipeline sklearn, ajusté séparément dans chaque fold pour éviter la fuite de données.

Métrique principale : F1 macro, qui donne le même poids aux trois espèces. Sélection sur validation croisée stratifiée à 5 folds du seul jeu d'entraînement. Le test reste isolé pendant les 8 essais Optuna. Seules les deux releases sont évaluées sur ce test après la sélection. Sur 30 exemples, un écart d'une prédiction change fortement le score : aucune conclusion de supériorité générale n'est justifiée.

- v1 : StandardScaler + régression logistique, C=1.
- Variations : régression logistique C=0,1 et SVM RBF C=1.
- v2 : meilleur des 8 essais Optuna (famille logistic/SVM et C entre 0,05 et 50).
- Optuna TPE : graine 42, 3 essais initiaux aléatoires, puis sélection adaptative.

La v2 sert à démontrer une mise à jour. Elle n'est pas promue automatiquement en production et n'est pas garantie meilleure sur le test. Les scores mesurés figurent dans `reports/comparison.json` et MLflow.

## Architecture et traçabilité

```text
Git : code + configuration + pointeur DVC
DVC : data/iris.csv <-> runtime/dvc-remote
ZenML : data_step -> train_step -> eval_step -> export_step
Optuna : 8 essais CV sur le train -> paramètres v2
MLflow : paramètres + métriques + modèles + matrices de confusion
Docker Compose : API FastAPI -> modèle v1 ou v2
```

Chaque release possède un fichier joblib et un manifeste JSON : hash SHA-256 des données, commit Git, hyperparamètres, métriques et identifiant MLflow. Le choix de release se fait au démarrage du processus via `MODEL_VERSION`. L'API garde le même contrat `/predict` quel que soit le modèle.

ZenML exécute réellement quatre pipelines à quatre étapes, avec cache désactivé pour enregistrer toutes les exécutions. MLflow reçoit les 8 essais Optuna et les 4 exécutions complètes. Les métadonnées ZenML sont persistées dans `runtime/zenml`.

## Données et DVC

```powershell
docker compose run --rm trainer python -m src.bootstrap
docker compose run --rm trainer dvc status
docker compose run --rm trainer dvc push
docker compose run --rm trainer dvc pull
```

Le remote est un dossier local, volontairement simple pour une démo autonome. `bootstrap` prouve un vrai téléchargement dans un dossier temporaire avec un cache DVC vide, puis compare les hashes SHA-256. Il ne se contente pas d'un pull utilisant le cache initial. Preuve : `evidence/dvc_push_pull.json`.

Le remote local n'est pas un stockage partagé. Dans un clone sur un autre PC, exécuter `setup.ps1` pour régénérer exactement Iris et remplir le remote. Pour un travail d'équipe, remplacer ce remote par un stockage S3/SSH partagé et y pousser les données. Aucun secret ne doit entrer dans Git.

## Commandes utiles

```powershell
# Réentraînement manuel / CT
docker compose run --rm trainer python -m src.train
# Contrôles
docker compose run --rm trainer ruff check src tests
docker compose run --rm trainer pytest -q
# Exécutions ZenML
docker compose run --rm trainer zenml pipeline runs list
# Mise à jour puis retour arrière
$env:MODEL_VERSION='v2'
docker compose up -d --wait --no-deps api
$env:MODEL_VERSION='v1'
docker compose up -d --wait --no-deps api
# Arrêt de cette stack uniquement
docker compose down
```

Le réentraînement manuel ajoute des runs MLflow et remplace les fichiers locaux des releases. Pour une vraie exploitation, conserver des releases immuables et imposer une validation avant promotion. Les compteurs de monitoring sont en mémoire et redémarrent avec l'API. Le redémarrage Compose entraîne une brève interruption : ce n'est pas un déploiement sans indisponibilité.

## CI GitLab

`.gitlab-ci.yml` propose lint, entraînement, tests, puis build et push de l'image dans le registre GitLab sur la branche principale. Le job de build nécessite un runner autorisant Docker-in-Docker en mode privilégié. Les variables du registre sont fournies par GitLab. Le pipeline distant doit être exécuté après publication du dépôt : une configuration présente ne constitue pas une preuve de CI exécutée.

L'image contient le code et l'environnement. Les modèles sont générés par le job d'entraînement et servis via le volume Compose. Ce projet ne prétend pas automatiser un déploiement distant. Un pipeline planifié GitLab relance le job test et constitue une simulation de CT.

## Organisation

```text
src/          données, pipeline, API, preuve DVC
tests/        séparation des jeux, reproductibilité, contrats v1/v2
scripts/      préparation et démo PowerShell
data/         CSV ignoré par Git + pointeur .dvc
models/       releases générées, ignorées par Git
reports/      résultats mesurés, figures et runs ZenML
evidence/     preuves DVC, déploiement et captures
docs/         guide oral et correspondance au cahier des charges
runtime/      stockage local persistant, ignoré par Git
```

## Dépôt à publier

Le dossier contient un dépôt Git local. Après création d'un dépôt vide dans ton compte, ajouter son URL et pousser les branches et tags :

```powershell
git remote add origin URL_DU_DEPOT
git push -u origin main
git push origin dev --tags
```

Le cahier des charges accepte un lien GitHub ou GitLab. GitLab permet aussi d'utiliser la CI fournie. L'URL distante doit être ajoutée au rendu une fois la publication effectuée.

## Références

- Iris / scikit-learn : https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html
- MLflow Tracking : https://mlflow.org/docs/latest/tracking/
- ZenML et cache : https://docs.zenml.io/concepts/steps_and_pipelines/advanced_features
- DVC remote : https://dvc.org/doc/command-reference/remote/add
- Optuna : https://optuna.readthedocs.io/en/stable/

Les dépendances principales sont fixées dans `requirements.txt`. L'environnement effectivement testé est exporté dans `requirements.lock.txt` lorsqu'il est disponible.
