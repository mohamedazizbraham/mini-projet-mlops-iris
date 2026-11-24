# Validation réalisée

- Construction de l'image Docker et installation de l'environnement : réalisées. Les versions exactes sont figées dans `requirements.lock.txt` ; pathspec 0.12.1 corrige l'incompatibilité rencontrée avec DVC.
- DVC : push puis pull dans un espace vierge avec cache vide. SHA-256 identique avant/après : `c52da941c4117668428d973554bb3380ba78c23400c2848e9b65107d63ccba47`.
- Optuna : 8 essais terminés. Meilleur essai : SVM RBF, C=7.851485442027691, F1 macro CV=0.974902.
- ZenML : 4 exécutions terminées, chacune avec data/train/eval/export. Les IDs figurent dans `reports/zenml_runs.json`.
- Tableau de bord ZenML : démarrage et authentification locale vérifiés. Son API retourne bien les 4 exécutions enregistrées.
- MLflow : 8 runs Optuna et 4 runs complets avec paramètres et métriques. Les releases possèdent un modèle et une matrice de confusion en artefacts.
- Tests : 4 tests réussis. Les 19 avertissements proviennent de dépréciations de bibliothèques, sans échec de test. Voir `evidence/tests.txt`.
- Lint : `ruff check src tests` réussi.
- Déploiement : requête HTTP réelle vers v1, puis v2, puis v1. Espèce retournée : setosa. Le rollback retrouve le même identifiant MLflow que le premier appel. Voir `evidence/deployment.json`.

| Release | F1 macro CV | F1 macro test | Accuracy test |
|---|---:|---:|---:|
| v1 | 0.957971 | 0.933333 | 0.933333 |
| v2 | 0.974902 | 0.966583 | 0.966667 |

Le test contient seulement 30 exemples : ce résultat ne démontre pas une supériorité générale de v2.

## Éléments non réalisés en ligne

La CI GitLab est fournie mais n'a pas été exécutée sur un runner distant. Les captures d'écran des interfaces MLflow/ZenML restent à ajouter : le contrôle du navigateur a été bloqué. Les exports et journaux fournis sont de vraies preuves d'exécution, pas des captures d'interface.
