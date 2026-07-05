---
title: "Rendu individuel — Gérard"
subtitle: "Projet Les Français face à l'information — M1 Big Data & IA"
author: "Gérard [TODO Nom de famille]"
date: "Juin 2026"
lang: fr
toc: true
toc-depth: 2
geometry: margin=2cm
---

\newpage

# 1. Mon périmètre dans le projet

Sur ce projet, j'ai assumé le rôle **Data / Qualité / Documentation** :

- **Pipeline Bronze** : ingestion brute des CSV INA avec encodage `latin-1`, génération de rapports qualité automatiques par dataset
- **Contrats pandera** (`pipeline_schemas.py`) : un schéma déclaratif par table Silver et Gold, contrôle des types, des bornes, des valeurs autorisées
- **Tests requêtes SQL** : vérification de la cohérence des données après chargement PostgreSQL (counts, intégrité référentielle)
- **Documentation utilisateur** : README projet, doc `docs/`, guide d'installation
- **Vérification métier des analyses avancées** : relecture critique des sorties clustering et ruptures (« est-ce que ça raconte une histoire crédible ? »)

L'objectif personnel : **garantir que les données livrées au dashboard sont propres et que le projet est reproductible** par quelqu'un qui le découvre.

\newpage

# 2. Perspectives d'évolution

## 2.1 Renforcer la suite de tests

Aujourd'hui, la validation pandera couvre les contrats de schéma mais pas la logique de transformation. À développer :

- **Tests unitaires pytest** sur chaque transformation Silver → Gold (jeux de données fixtures, assertions sur les agrégats attendus)
- **Tests d'intégration** : exécuter le pipeline complet sur un sous-ensemble (1000 lignes) et vérifier que les sorties Gold respectent les invariants métier
- **Tests de régression** : conserver des « snapshots » des tables Gold à un instant T et alerter si une transformation les modifie

Cible : couverture > 80 % sur le pipeline data, intégrée à GitHub Actions.

## 2.2 CI/CD GitHub Actions

Workflow envisagé :

1. **Sur push / PR** :
   - flake8 + black sur le code Python
   - pytest avec rapport de couverture
   - validation des schémas pandera sur un échantillon
2. **Sur merge dans main** :
   - build du pipeline complet
   - publication des tables Gold sur un bucket S3 ou un release GitHub
   - déploiement Streamlit Cloud automatique

## 2.3 Monitoring qualité en continu

Une fois le projet déployé :

- **Alertes** sur les violations de schéma (e.g. taux de parité > 100 %)
- **Tableau de bord qualité** : nb de lignes par table par exécution, % de valeurs manquantes, dérive vs baseline
- **Logs structurés** centralisés (Loki ou simple fichier rolling) au lieu du `logs/pipeline.log` actuel

## 2.4 Documentation technique enrichie

- **Diagrammes interactifs** dans la doc (passer de Mermaid statique à des SVG ou diagrams.net)
- **Tutoriel pas à pas** pour un nouvel arrivant : « ajouter un dataset au pipeline »
- **Schema des contrats pandera** exporté en JSON Schema pour réutilisation côté Django

## 2.5 Publication sur data.gouv.fr

Le cahier des charges encourage la publication d'une « réutilisation » sur `data.gouv.fr`. Concrètement : créer une fiche réutilisation, lier les datasets sources INA, joindre le repo GitHub et un lien vers le dashboard déployé. Cela exige une **fiche de méthodologie publique** que je peux porter.

\newpage

# 3. Analyse critique des limites techniques rencontrées

## 3.1 Tests insuffisants au début

Pendant les deux premiers mois, je me suis appuyé exclusivement sur pandera pour valider les transformations. C'est une bonne base mais ce n'est pas un test : pandera ne vérifie pas qu'un `groupby + sum` agrège *correctement*, seulement que les types de la sortie sont conformes. **Conséquence** : un bug d'agrégation découvert tardivement (un `mean` au lieu d'un `sum` sur une métrique) a nécessité de retraiter la Gold complète.

## 3.2 Documentation produite à la fin

J'ai documenté progressivement le `CLAUDE.md` (qui sert de contexte agent), mais la **vraie documentation utilisateur** a attendu juin. Conséquence : pendant 4 mois, un nouvel arrivant aurait galéré à lancer le projet. À refaire : documenter en flux tendu plutôt qu'en rattrapage.

## 3.3 Encodage latin-1 mal géré au départ

J'ai laissé passer plusieurs jours d'erreurs silencieuses sur les accents avant de remonter le problème jusqu'à `encoding="latin-1"`. La détection aurait dû être faite dès le `head()` sur le DataFrame. Leçon : **EDA = ouvrir, regarder, valider sur 100 lignes, pas seulement compter**.

## 3.4 Rapports qualité Bronze utilisés à moitié

Les rapports qualité sont générés à chaque ingestion mais peu consultés en pratique. Idéalement : ils devraient être versionnés et comparés d'une exécution à l'autre pour détecter une dérive de la source.

## 3.5 Gestion des doublons « silencieuse »

La déduplication Silver est tracée (nb de doublons logué) mais pas remontée à l'utilisateur du dashboard. Si un dataset source change et introduit des doublons en masse, on les supprimera sans alerte visible. Une alerte dans le dashboard serait pertinente.

\newpage

# 4. Documentation utilisateur

Voir `07_documentation_utilisateur.md`. Sections que j'ai rédigées :

- Installation des dépendances et prérequis (Python, PostgreSQL)
- Lancement du pipeline complet
- Format et signification de chaque table Gold
- Codes erreur fréquents et leur résolution
- Comment ajouter un nouveau dataset au pipeline

\newpage

# 5. Analyse personnelle

## 5.1 Défis rencontrés

**Trouver ma valeur ajoutée en tant que « QA » dans un projet data.**
Au démarrage, mon rôle était flou : ni dev pur, ni data scientist. J'ai progressivement compris que la qualité n'est pas une étape, c'est un fil rouge — et que mon rôle était de **construire les filets de sécurité** (rapports qualité, contrats pandera, tests) qui permettent aux autres de coder vite sans tout casser. Cette posture s'est révélée précieuse, mais je l'ai trouvée tard.

**Documenter pour un public qui n'existe pas encore.**
J'ai longtemps repoussé la rédaction de la doc utilisateur en me disant « personne ne va la lire ». Quand on a essayé de faire tourner le projet sur la machine d'un proche, on a mis 1h30 à comprendre pourquoi `make pipeline` plantait. Depuis, je suis plus rigoureux sur la doc d'installation.

**pandera : courbe d'apprentissage.**
La syntaxe pandera n'est pas intuitive (DataFrameSchema, Column, Check). Il m'a fallu plusieurs essais pour comprendre comment composer les checks. Une fois acquis, c'est devenu un outil que je veux utiliser dans tous mes projets data.

## 5.2 Forces personnelles identifiées

- **Curiosité méthodologique** : j'ai lu en parallèle sur les pratiques de Data Quality (Great Expectations, Soda) et apporté ces réflexions à l'équipe
- **Rigueur dans la documentation** : préfère un README clair et concis à du code « trop intelligent »
- **Capacité à challenger les sorties** : remonter à mes coéquipiers « ce résultat est-il crédible ? » plutôt que de prendre les outputs ML pour argent comptant

## 5.3 Faiblesses identifiées

- **Lenteur à coder** : je passe plus de temps que nécessaire à raffiner avant de pousser. À l'inverse, mes commits sont propres.
- **Manque d'aisance avec scikit-learn** : je peux exécuter les analyses faites par Lucas mais j'aurais du mal à les construire seul
- **Peu d'expérience frontend** : je n'ai contribué que ponctuellement au dashboard, alors que mes feedbacks « utilisateur » auraient pu y être plus présents tôt

## 5.4 Compétences développées

| Compétence | Niveau avant | Niveau après |
|---|---|---|
| pandera (DataFrameSchema, Check) | Inconnu | Intermédiaire |
| Tests pytest sur pipeline data | Théorique | Pratique |
| EDA structurée | Débutant | Intermédiaire |
| Documentation technique (README, guides) | Intermédiaire | Confirmé |
| PostgreSQL (vérifications, requêtes test) | Intermédiaire | Confirmé |
| Lecture critique de sorties ML | Débutant | Intermédiaire |
| Logs structurés, rapports qualité | Débutant | Intermédiaire |

## 5.5 Axes d'amélioration pour de futurs projets

1. **Tests avant code** : adopter une discipline plus stricte (TDD partiel sur les transformations data).
2. **Documentation en parallèle du dev**, pas en rattrapage : un nouveau composant = une section de doc immédiate.
3. **Tester le démarrage projet sur une machine vierge** dès la première semaine, pas trois mois plus tard.
4. **Monter en compétence sur scikit-learn** pour pouvoir relire le code de mes coéquipiers, pas seulement leurs résultats.
5. **Contribuer plus tôt au frontend** : mon regard « débutant » sur la donnée est précieux pour un dashboard grand public.
6. **Industrialiser la qualité** : passer d'un rapport qualité ponctuel à un monitoring continu (Great Expectations, dérive vs baseline).
