# Données sources

Les CSVs de ce dossier sont les **données brutes originales** du projet. Elles sont consommées par `pipeline.py` pour produire les couches Bronze, Silver et Gold.

## Fichiers versionnés dans Git

| Fichier | Source | Description |
|---|---|---|
| `ina-barometre-jt-tv-donnees-quotidiennes-2000-2020-nbre-sujets-durees-202410.csv` | [INA — Baromètre JT](https://www.ina.fr/institut-national-audiovisuel/statistiques) | Thèmes quotidiens des JT 2000-2020 |
| `20190308-years.csv` | INA — Open Data parité | Agrégats annuels parité H/F par chaîne |
| `20190308-hourstatall.csv` | INA — Open Data parité | Stats horaires parité H/F par année |
| `20190308-radio-years.csv` | INA — Open Data parité | Taux expression femmes par station radio |
| `20190308-tv-years.csv` | INA — Open Data parité | Taux expression femmes par chaîne TV |
| `evenements_france.csv` | Construit manuellement | Dates clés 2000-2020 pour contextualiser les pics thématiques |

## Fichier NON versionné (> 100 MB)

| Fichier | Taille | Comment l'obtenir |
|---|---|---|
| `20190308-stats.csv` | ~109 MB | Télécharger depuis INA Open Data, ou demander à l'équipe via Drive partagé |

Une fois placé dans `data/raw/`, relancer `python pipeline.py` pour regénérer les couches Silver et Gold dépendantes.

## Remarques sur les formats

- **INA JT** : séparateur `;`, encodage `latin-1`, **pas d'en-tête** (colonnes : date, chaîne, code_catégorie_vide, rubrique, nb_sujets, durée_totale_sec)
- **Autres fichiers** : séparateur `,`, encodage `utf-8`, en-tête sur la 1re ligne
- **Format wide** : `radio-years.csv` et `tv-years.csv` sont en format large (une colonne par station/chaîne) — le pipeline les unpivot en format long
