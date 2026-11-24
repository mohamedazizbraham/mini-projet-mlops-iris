# Oral court : 5 minutes ou 8 à 10 minutes

## Avant de présenter

Faire tourner `scripts/setup.ps1` avant le cours. Garder Docker Desktop ouvert. Ouvrir MLflow sur http://localhost:5500 et la documentation API sur http://localhost:8500/docs. Préparer PowerShell dans le dossier du projet avec la commande `powershell -ExecutionPolicy Bypass -File scripts/demo.ps1`, sans encore la lancer. Afficher le support de présentation.

Ne pas construire d'image ni réentraîner pendant la démo. Les résultats dans `reports/` et les preuves dans `evidence/` servent de secours. Les captures d'interface restent à ajouter selon `docs/CAPTURES_A_PRENDRE.md`.

## Version 5 minutes

**0:00 à 0:30 — Objectif.** « Mon projet classe une fleur Iris à partir de quatre mesures. Le modèle est volontairement léger : le sujet principal est de rendre son entraînement traçable et de pouvoir changer de version sans changer l'API. »

**0:30 à 1:20 — Architecture.** « Git conserve le code. DVC versionne le fichier de données. ZenML exécute les étapes data, train, eval et export. MLflow garde les paramètres, les scores et les modèles. Docker Compose lance l'API. Chaque modèle possède un manifeste qui relie le hash des données, le commit Git et le run MLflow. »

**1:20 à 2:00 — Expériences.** « La baseline est une régression logistique. J'ai ajouté deux variations et huit essais Optuna. Je compare le F1 macro en validation croisée, uniquement sur les 120 exemples d'entraînement. Les 30 exemples de test ne participent pas à la sélection. Les scores réels sont dans ce tableau. Sur un dataset aussi petit, je ne prétends pas qu'une faible différence prouve une meilleure généralisation. »

**2:00 à 4:00 — Démo.** Exécuter `scripts/demo.ps1`.

1. Première Entrée : « L'API prédit setosa avec v1. La réponse expose la version et l'identifiant de son expérience. »
2. Deuxième Entrée : « Je passe à v2. Le contrat et les données envoyées restent identiques. Le numéro de version et le run changent. »
3. Troisième Entrée : « Je reviens à v1. On retrouve exactement le run initial. Le script vérifie ces conditions et sauvegarde la preuve. »

**4:00 à 5:00 — Preuves et limites.** « Le push/pull DVC a été testé dans un espace vide, avec comparaison des hashes. Quatre runs ZenML et les expériences MLflow ont été exécutés. Le projet inclut une CI GitLab prête à lancer après publication. Le remote DVC est local et le redémarrage provoque une courte interruption : il s'agit d'une démonstration locale, pas d'une plateforme de production. »

## Pour atteindre 8 à 10 minutes

Ajouter une minute sur la comparaison MLflow : filtrer les runs v1, variation-low-C, variation-svm et v2, puis afficher leurs paramètres et F1 CV. Ajouter une minute sur un run ZenML et ses quatre étapes. Expliquer pendant une minute la preuve DVC : restauration depuis le remote dans un dossier temporaire sans le cache d'origine. Garder la même démo courte et laisser le temps aux questions.

## Questions probables

**Pourquoi Iris ?** Public, léger et entraînable sur CPU. Il permet de se concentrer sur le workflow MLOps.

**Git et DVC font-ils la même chose ?** Git garde les fichiers de code et les petits pointeurs DVC. DVC stocke les données par leur contenu dans un cache et un remote.

**MLflow et ZenML font-ils la même chose ?** ZenML orchestre l'ordre des étapes et garde leurs exécutions. MLflow facilite la comparaison des expériences et conserve leurs artefacts.

**Pourquoi F1 macro ?** Il mesure la qualité de classification en pondérant chaque classe de la même façon. Ici les classes sont équilibrées, donc l'accuracy est également utile.

**Comment éviter la fuite de données ?** Split fixe avant recherche, scaler intégré au pipeline de chaque fold, test exclu des essais Optuna.

**Pourquoi la prédiction peut-elle rester identique en v2 ?** Deux modèles peuvent classer la même fleur correctement. La preuve du changement est la version et l'identifiant du run, pas l'obligation d'obtenir une autre espèce.

**Pourquoi un rollback ?** Pour revenir rapidement à un artefact connu si une nouvelle version pose problème, sans réentraîner.

**La CI a-t-elle tourné en ligne ?** Répondre selon l'état réel du dépôt. Les tests locaux et la configuration CI ne prouvent pas une exécution sur GitLab.

**Limites ?** Petit test, remote local, absence de haute disponibilité, artefacts locaux remplaçables lors du réentraînement, monitoring en mémoire. Pour aller plus loin : stockage partagé, registre de modèles immuables, seuil de promotion et déploiement sans interruption.
