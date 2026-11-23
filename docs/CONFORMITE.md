# Correspondance au cahier des charges

| Exigence | Réalisation | Preuve à consulter |
|---|---|---|
| Dataset public et léger | Iris, 150 lignes, fourni par scikit-learn | src/data.py, data/iris.csv.dvc |
| Baseline mesurable | Régression logistique, F1 macro | reports/comparison.json |
| Git | Dépôt local, branches main/dev, tags v1/v2 à finalisation | git log, git branch, git tag |
| Docker / Compose | Image commune, API et MLflow, outils d'entraînement | Dockerfile, docker-compose.yml |
| Versioning DVC | Pointeur du dataset et remote local | .dvc/config, data/iris.csv.dvc |
| Push / pull reproductible | Restauration dans un espace vierge, SHA-256 identique | evidence/dvc_push_pull.json |
| MLflow | Baseline, variations, Optuna, modèles et figures | UI port 5500, evidence/, reports/ |
| ZenML | Quatre exécutions, data/train/eval/export | reports/zenml_runs.json, captures |
| Optuna | 8 essais, modèle et C, objectif F1 CV | reports/optuna_trials.csv |
| CI GitLab optionnelle | Lint/tests puis build/push registre | .gitlab-ci.yml ; exécution distante à confirmer |
| API stable | POST /predict, validation des 4 mesures | src/api.py, tests/test_project.py |
| Update et rollback | v1, v2, v1 avec vérification des run IDs | scripts/demo.ps1, evidence/deployment.json |
| Monitoring bonus | Nombre de requêtes, erreurs, latence moyenne | GET /metrics |
| CT simple | Réentraînement manuel, CI planifiable | python -m src.train |
| Documentation | Exécution, architecture, protocole, limites | README.md, docs/ORAL.md |

Les tags Git identifient des états du code. Les releases du modèle sont identifiées par leur manifeste et leur run MLflow. Ces identifiants répondent à des besoins différents et ne doivent pas être confondus.

Les preuves dans ce dossier doivent être celles de l'exécution effective. Une configuration CI prête n'est pas une preuve de CI distante exécutée. Le remote DVC local répond à la démonstration push/pull mais n'est pas partagé entre postes.
