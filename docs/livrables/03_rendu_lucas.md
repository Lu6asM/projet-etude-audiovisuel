---
title: "Rendu individuel — Lucas"
subtitle: "Projet Les Français face à l'information — M1 Big Data & IA"
author: "Lucas [TODO Nom de famille]"
date: "Juin 2026"
lang: fr
toc: true
toc-depth: 2
geometry: margin=2cm
---

\newpage

# 1. Mon périmètre dans le projet

Sur ce projet, j'ai assumé le rôle **Data / Frontend** :

- **Exploration initiale (EDA)** des 7 datasets INA (volumétrie, qualité, doublons, encodage)
- **Pipeline Silver et Gold** : typage strict, validation pandera, agrégation en 6 tables analytiques
- **Analyses avancées** : implémentation de la détection de ruptures (PELT), du clustering ACP + k-means, des corrélations Pearson + p-values
- **Dashboard Streamlit** : architecture en 5 pages, palette graphique cohérente, accessibilité grand public

L'objectif personnel que je m'étais fixé en début de projet : produire un **MVP de bout en bout** qui puisse être consulté autant par un chercheur que par un citoyen. Cet objectif est atteint sur le dashboard livré.

\newpage

# 2. Perspectives d'évolution

Le projet livré couvre solidement les axes 1 et 2 du défi Open Data University. Plusieurs directions d'évolution restent ouvertes.

## 2.1 Sur le pipeline data

- **Passage à Parquet** pour les couches Silver/Gold : les CSV deviennent lourds à recharger en cache (~100 Mo de données) ; Parquet offrirait un gain de lecture × 5-10 et un schéma typé persistant.
- **dbt** ou **dlt** pour orchestrer le pipeline : aujourd'hui les transformations sont des fonctions Python orchestrées par `pipeline.py`. Un orchestrateur déclaratif rendrait le DAG plus lisible et permettrait des tests unitaires par modèle.
- **Incrémentalité** : le pipeline reconstruit tout à chaque exécution. Avec un orchestrateur, on pourrait ne retraiter que les partitions modifiées.

## 2.2 Sur les analyses avancées

- **Modélisation supervisée** : à partir des profils thématiques + parité, prédire la chaîne à partir de signatures éditoriales (problème de classification multi-classes). Permettrait de valider quantitativement les archétypes détectés par clustering.
- **Topic modeling sur les titres de sujets** (si on récupère les textes) avec BERTopic ou LDA, pour décomposer la rubrique « Société » en sous-thèmes plus fins.
- **Modèle temporel** type ARIMA ou Prophet pour projeter les tendances futures par rubrique.

## 2.3 Sur le frontend

- **Déploiement Streamlit Community Cloud** pour rendre le dashboard accessible publiquement. Cible : une URL `lesfrancaisfaceainfo.streamlit.app`.
- **Migration partielle vers React + Chart.js** pour les pages les plus consultées si on souhaite un branding fort (le défi est porté par data.gouv.fr et un look « État français » serait pertinent).
- **Ajout de la page Axe 3** (rapport des Français à l'info, sondages ARCOM) — actuellement hors scope assumé, mais documentée comme évolution naturelle.

## 2.4 Sur l'industrialisation

- **Containerisation Docker** : `Dockerfile` + `docker-compose.yml` pour empaqueter pipeline + Streamlit + PostgreSQL.
- **CI/CD GitHub Actions** : tests pandera + flake8 + déploiement Streamlit Cloud automatique sur push `main`.
- **Publication sur data.gouv.fr** comme réutilisation, conformément à l'invitation explicite du cahier des charges Open Data University.

\newpage

# 3. Analyse critique des limites techniques rencontrées

## 3.1 Encodage des sources INA

Les CSV sont fournis en `latin-1`, ce qui a généré des erreurs silencieuses au début (les accents devenaient des caractères imprévus). Détecté tôt grâce à la phase EDA, géré uniformément par `encoding="latin-1"` au chargement. **Leçon retenue** : tester l'encodage *avant* le typage, sinon on s'arrache les cheveux à debug des erreurs aval.

## 3.2 Données radio thématiquement absentes

L'INA fournit la **parité radio** par année et par station, mais **pas les thèmes radio** : impossible donc d'étendre l'analyse « thèmes × parité » à la radio. Conséquence : le cœur du projet (page *Thèmes × Parité*) est TV-only. **Limite assumée et documentée** dans le dashboard.

## 3.3 Période d'intersection TV thèmes × parité

Les thèmes JT couvrent 2000-2020, la parité TV couvre 1995-2018. L'intersection exploitable est **2010-2019**, ce qui réduit la taille de l'échantillon pour les corrélations. Les p-values restent significatives pour les corrélations fortes, mais une période plus longue (notamment plus de données après 2019) renforcerait la robustesse.

## 3.4 Cache Streamlit et taille des données

`st.cache_data` est très efficace, mais sur les premières versions le rechargement initial prenait ~5 secondes. La parade : charger uniquement les colonnes utiles + envisager Parquet (voir § 2.1).

## 3.5 Choix de la pénalité PELT

L'algorithme PELT prend une pénalité (`pen`) qui pilote le nombre de ruptures détectées. J'ai choisi empiriquement une valeur par essais, en regardant si les ruptures détectées correspondaient à des événements connus (COVID, attentats 2015). Une méthode plus robuste : la **règle BIC** ou une **validation croisée**, à implémenter dans une version future.

## 3.6 Choix de k=3 pour le clustering

Le coude de l'inertie n'était pas franc entre k=2, k=3 et k=4. J'ai tranché à k=3 sur un critère d'interprétabilité (3 archétypes lisibles), mais l'argumentation reste qualitative. Une **silhouette analysis** ou **Calinski-Harabasz** plus rigoureuse serait souhaitable.

\newpage

# 4. Documentation utilisateur

La documentation utilisateur complète est dans `07_documentation_utilisateur.md`. Résumé :

## Installation
```bash
git clone <repo>
cd Projet-detude
make install
```

## Lancement du pipeline
```bash
make pipeline   # Bronze → Silver → Gold
make analyses   # Ruptures + clustering + corrélations
make dashboard  # Streamlit sur localhost:8501
```

## Navigation dans le dashboard

5 pages dans la sidebar, chacune avec ses tabs internes. Tous les graphes principaux disposent d'un **dépliant « Comment lire ce graphique ? »** rédigé pour un public non technicien.

\newpage

# 5. Analyse personnelle

## 5.1 Défis rencontrés

**Pédagogie de la donnée pour grand public.**
Le défi explicite était de rendre les résultats utilisables par un citoyen sans formation statistique. C'est un exercice plus difficile qu'il n'y paraît : il a fallu reformuler à plusieurs reprises les explications (la version initiale parlait de « corrélation de Pearson » sans la définir), tester sur des proches non techniques, et accepter de simplifier au prix d'une perte de précision technique. Ça m'a appris que la **vulgarisation est une compétence à part entière**, pas un simple sous-produit de la maîtrise technique.

**Architecture médaillon en équipe.**
J'avais lu sur le pattern Bronze/Silver/Gold mais jamais appliqué dans un projet d'équipe. La question « où mettre cette transformation ? » s'est posée à chaque ajout. La règle qu'on a fini par adopter : *Bronze ne fait que lire, Silver garantit que les données sont propres, Gold prépare exactement ce que la couche conso attend*. Cette discipline a payé : les bugs sont restés localisés.

**Streamlit et la stack frontend dans la durée.**
Streamlit donne envie d'ajouter des composants en permanence. J'ai dû refactor plusieurs fois (réduction de 12 à 5 onglets, remplacement de mes CSS par `style_metric_cards`, replacement de mes téléchargements custom par `chart_container`). La leçon : **commencer par fonctionner, polir ensuite**, plutôt que de tout designer du premier coup.

## 5.2 Forces personnelles identifiées

- **Capacité à itérer rapidement** sur un MVP : passer d'un dashboard brut à un livrable narratif en plusieurs passes courtes
- **Lecture critique du cahier des charges** : repérer ce qui est obligatoire vs souhaité (différence cadre péda / défi)
- **Pédagogie de la data** : reformuler du jargon en langage accessible

## 5.3 Faiblesses identifiées

- **Tendance à sur-optimiser tôt** : j'ai passé du temps sur le template Plotly avant de savoir si le contenu était bon. À l'avenir, finir le contenu avant de styliser.
- **Connaissance superficielle de Django REST** : sur ce projet j'ai laissé le backend à Baptiste, mais je devrais combler ce gap pour pouvoir contribuer transversalement la prochaine fois.
- **Manque de rigueur sur les tests unitaires côté pipeline** : la validation pandera couvre les schémas, mais pas les transformations métier. Une suite pytest aurait sécurisé les refactos.

## 5.4 Compétences développées

| Compétence | Niveau avant | Niveau après |
|---|---|---|
| pandas avancé (groupby, melt, pivot) | Intermédiaire | Confirmé |
| pandera et contrats de schéma | Débutant | Intermédiaire |
| scikit-learn (PCA + k-means) | Théorique | Pratique |
| `ruptures` (PELT) | Inconnu | Pratique |
| Streamlit (cache, layout, composants) | Débutant | Confirmé |
| Plotly Express + Graph Objects | Intermédiaire | Confirmé |
| Architecture médaillon | Théorique | Pratique en équipe |
| Vulgarisation data | Débutant | Intermédiaire |

## 5.5 Axes d'amélioration pour de futurs projets

1. **Écrire les tests d'abord** sur les transformations métier — la validation de schéma ne suffit pas.
2. **Boucler avec les utilisateurs finaux dès le MVP** plutôt qu'attendre la version finale pour faire relire.
3. **Apprendre Django REST en profondeur** pour ne plus être dépendant d'un coéquipier sur le backend.
4. **Documenter en cours de route**, pas à la fin : le `CLAUDE.md` du projet (qui sert d'agent context) a été précieux, mais une vraie doc utilisateur a manqué pendant 3 mois.
5. **Versionner les datasets** (DVC, lakeFS) plutôt que de garder des CSV dans Git : le repo a grossi vite et les commits de données polluent l'historique.
