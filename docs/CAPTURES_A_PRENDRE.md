# Captures d'interface à ajouter au rendu

Les exécutions et preuves JSON/CSV ont été réalisées. Les captures d'écran des interfaces n'ont pas pu être prises automatiquement : le contrôle du navigateur a été bloqué. Ne pas présenter les exports comme des captures d'interface.

1. Ouvrir http://localhost:5500, sélectionner Iris-MLOps et capturer la liste des 12 runs.
2. Cocher v1 et v2, choisir Compare, puis capturer les paramètres et les métriques.
3. Après entraînement, lancer `docker compose --profile tools up -d zenml`. Ouvrir http://localhost:8501, puis capturer les quatre exécutions et le graphe d'un run.

Enregistrer les images dans `evidence/`. Les fichiers `reports/comparison.json`, `reports/optuna_trials.csv`, `reports/zenml_runs.json`, `evidence/dvc_push_pull.json` et `evidence/deployment.json` fournissent les résultats mesurés, indépendamment des captures.
