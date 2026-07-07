# Guide de déploiement : Django et Apache Airflow avec Docker Compose

Ce guide explique comment configurer, structurer et lancer conjointement votre application **Django** et votre cluster **Apache Airflow 3.2.2** en utilisant **Docker Compose**.

---

# 1. Structure recommandée du projet

Pour éviter les conflits de ports (les deux projets utilisant PostgreSQL sur le port **5432** par défaut) ou de volumes, il est fortement recommandé d'organiser votre projet avec deux dossiers distincts.

```text
├── Django/                  # Dossier pour votre application Django
│   ├── Dockerfile               # Votre Dockerfile Django
│   ├── requirements.txt         # Dépendances Django
│   ├── manage.py
│   ├── config/                  # Configuration Django
│   ├── dashboard/               # Le dashboard d'affichage Django avec les APIs
│   └── docker-compose.yaml      # Fichier Compose pour Django
│
└── Airflow/                 # Dossier dédié à Airflow
    ├── docker-compose.yaml      # Fichier Compose officiel d'Airflow
    ├── .env                     # Variables d'environnement Airflow
    ├── dags/                    # Vos DAGs Python
    ├── logs/                    # Logs générés par Airflow
    ├── config/                  # Configuration personnalisée
    └── plugins/                 # Plugins Airflow
```

---

# 2. Configuration et lancement de Django

## Étape 2.1 : Validation des fichiers

Placez-vous dans le dossier **`Django/`**.

Vérifiez que :

- votre `Dockerfile` contient bien la configuration basée sur **Python 3.11-slim** ;
- votre fichier `docker-compose.yaml` est bien présent dans ce dossier.

---

## Étape 2.2 : Initialisation de Django

Depuis le dossier **`Django/`**, exécutez les commandes suivantes.

### Construire et démarrer les conteneurs

```bash
docker compose up -d --build
```



Une fois cette étape terminée, votre application Django est accessible à l'adresse :

```
http://localhost:8000
```

Cependant il vous manquera les données pour que l'affichage du dashboard fonctionne


---
# 3. Structure PostgreSQL
Ensuite connectez vous sur votre base de donnée contenue dans votre conteneur via les informations ci-dessous:

```
- POSTGRES_DB=mon_projet_db
- POSTGRES_USER=mon_utilisateur
- POSTGRES_PASSWORD=mon_mot_de_passe
```

Puis exécutez le script SQL contenu dans ce dossier, cela créera la structure de la base de donnée.

---

# 4. Configuration et lancement d'Apache Airflow

Le fichier **Docker Compose** fourni pour Airflow utilise l'exécuteur **Celery**.

Il nécessite plusieurs variables d'environnement indispensables, notamment une **clé Fernet** permettant le chiffrement des données sensibles.

---

## Étape 4.1 : Création du fichier `.env`

Ouvrez un terminal dans le dossier **`Airflow/`**.

Créez un fichier nommé **`.env`**.

### Sous Linux / macOS

Insérez le contenu :

```bash
AIRFLOW_UID=50000
```

### Sous Windows

Si vous êtes sous Windows (ou si Python n'est pas installé localement), créez manuellement le fichier `.env` avec le contenu suivant :

```env
AIRFLOW_UID=50000
```

---

## Étape 4.2 : Initialisation de la base Airflow

Avant de démarrer Airflow, il faut exécuter le service **`airflow-init`**, qui :

- initialise la base de données PostgreSQL ;
- crée les tables nécessaires ;
- crée le compte administrateur.

Depuis le dossier **`Airflow/`**, exécutez :

```bash
docker compose up airflow-init
```

Attendez la fin de l'exécution.

Le conteneur doit s'arrêter avec un message similaire à :

```text
exited with code 0
```

---

## Étape 4.3 : Démarrage du cluster Airflow

Une fois l'initialisation terminée, lancez tous les services en arrière-plan :

```bash
docker compose up -d
```

L'interface web d'Airflow est ensuite disponible à l'adresse :

```
http://localhost:8080
```

Identifiants par défaut :

- **Utilisateur :** `airflow`
- **Mot de passe :** `airflow`


## Étape 4.4 : Connexion a la BD

Allez dans la section **ADMIN** -> **CONNEXION**

Et créez une nouvelle connexion appelée **postgres_projet_conn** avec les valeurs:

```
- ID de Connexion : postgres_projet_conn
- Type de connexion: Postgres
- Hote: host.docker.internal
- identifiant: mon_utilisateur
- Mot de passe: mon_mot_de_passe
- Port: 5432
- Databas: mon_projet_db
```

Pour vérifier que la connexion a bien été rentrée, allez dans **DAGS** et lancez le dag **aa__test__connexion__postgres**

Puis lancez le DAG **pipeline_audiovisuel_dynamique**

Vous avez terminé





