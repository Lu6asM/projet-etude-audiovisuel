# Diagrammes du projet

À insérer dans le rendu groupe et dans la vidéo (screenshots).
Les diagrammes Mermaid se rendent nativement sur GitHub, dans VS Code (extension Markdown Preview Mermaid), et dans Pandoc avec `mermaid-filter`.

---

## 1. Architecture médaillon Bronze → Silver → Gold

```mermaid
flowchart LR
    subgraph SOURCES["📦 Sources INA (Open Data)"]
        S1[ina-barometre-jt<br/>thèmes JT quotidiens]
        S2[20190308-stats<br/>parole H/F par chaîne]
        S3[20190308-years<br/>agrégats annuels]
        S4[20190308-hourstatall<br/>stats horaires]
        S5[20190308-radio-years<br/>parité radio]
        S6[20190308-tv-years<br/>parité TV]
        S7[evenements_france<br/>référentiel manuel]
    end

    subgraph BRONZE["🥉 BRONZE - Ingestion brute"]
        B1[Lecture CSV<br/>encodage latin-1]
        B2[Rapport qualité<br/>nulls, dupes, types]
    end

    subgraph SILVER["🥈 SILVER - Nettoyage et typage"]
        SI1[Cast types,<br/>parsing dates]
        SI2[Validation pandera]
        SI3[Suppression doublons]
        SI4[Enrichissement<br/>annee, mois, jour_semaine]
    end

    subgraph GOLD["🥇 GOLD - 6 tables analytiques"]
        G1[tv_theme_parite]
        G2[parite_unifiee]
        G3[stats_prime_time]
        G4[themes_evenements]
        G5[saisonnalite]
        G6[parite_ranking]
    end

    subgraph CONSO["🎯 Consommation"]
        D1[Streamlit dashboard]
        D2[PostgreSQL + Django<br/>API REST]
        D3[Analyses avancées<br/>ruptures / clustering / corrélations]
    end

    SOURCES --> BRONZE --> SILVER --> GOLD --> CONSO

    style BRONZE fill:#cd7f32,color:#fff
    style SILVER fill:#c0c0c0,color:#000
    style GOLD fill:#ffd700,color:#000
    style CONSO fill:#6366f1,color:#fff
```

---

## 2. Pipeline data → IA → décision

```mermaid
flowchart TB
    A[CSV sources INA] --> B[Bronze<br/>ingestion]
    B --> C[Silver<br/>typage, pandera, dédoublonnage]
    C --> D[Gold<br/>6 tables analytiques]
    D --> E1[Analyses statistiques<br/>Pearson, agrégats]
    D --> E2[Détection de ruptures<br/>algorithme PELT]
    D --> E3[Apprentissage non supervisé<br/>ACP + k-means]
    E1 --> F[Dashboard Streamlit]
    E2 --> F
    E3 --> F
    F --> G[Décision et plaidoyer<br/>citoyens, associations, pouvoirs publics]

    style E1 fill:#10b981,color:#fff
    style E2 fill:#10b981,color:#fff
    style E3 fill:#10b981,color:#fff
    style F fill:#6366f1,color:#fff
    style G fill:#f59e0b,color:#fff
```

---

## 3. Schéma relationnel PostgreSQL

```mermaid
erDiagram
    CHANNELS ||--o{ DAILY_STATS : "diffuse"
    THEMES ||--o{ DAILY_STATS : "catégorise"
    CHANNELS ||--o{ YEARLY_GENDER : "mesure parité"
    CHANNELS ||--o{ HOURLY_STATS : "par tranche horaire"

    CHANNELS {
        int id PK
        string name UK
        string media_type
        bool is_public
    }
    THEMES {
        int id PK
        string label UK
        string category
    }
    DAILY_STATS {
        int id PK
        date jour
        int channel_id FK
        int theme_id FK
        int nb_subjects
        int duration_sec
    }
    YEARLY_GENDER {
        int id PK
        int year
        int channel_id FK
        float women_expression_rate
        float speech_rate
    }
    HOURLY_STATS {
        int id PK
        int year
        int channel_id FK
        int hour
        float male_duration
        float female_duration
    }
```

---

## 4. Organisation de l'équipe

```mermaid
flowchart LR
    subgraph EQUIPE["Équipe projet"]
        L["👨‍💻 Lucas<br/>Data + Streamlit + Pipeline"]
        B["👨‍💻 Baptiste<br/>Lead Backend Django/PostgreSQL"]
        G["👨‍💻 Gérard<br/>Data + Tests + Documentation"]
    end

    subgraph LIVRABLES["Livrables"]
        D1[Pipeline médaillon]
        D2[Analyses avancées IA]
        D3[Dashboard Streamlit]
        D4[Backend PostgreSQL]
        D5[Tests et doc qualité]
    end

    L --> D1
    L --> D2
    L --> D3
    B --> D4
    G --> D5
    G --> D1
```

---

## 5. Cycle de vie d'une donnée (exemple)

```mermaid
sequenceDiagram
    participant CSV as Fichier CSV INA
    participant Bronze as Couche Bronze
    participant Silver as Couche Silver
    participant Gold as Couche Gold
    participant App as Dashboard
    participant User as Utilisateur

    CSV->>Bronze: Lecture brute (latin-1)
    Bronze->>Bronze: Génère rapport qualité
    Bronze->>Silver: Cast types, parsing dates
    Silver->>Silver: Validation pandera
    Silver->>Silver: Drop duplicates
    Silver->>Gold: Agrégation, jointure thèmes×parité
    Gold->>Gold: Validation pandera Gold
    Gold->>App: Lecture cache st.cache_data
    App->>App: Calcul Pearson, PCA, k-means
    App->>User: Visualisation Plotly + explications
    User->>App: Filtre période, sélection rubrique
    App->>User: Mise à jour réactive
```

---

## 6. Architecture de déploiement (cible)

```mermaid
flowchart TB
    subgraph DEV["💻 Développement local"]
        Code[Code Python]
        Make[Makefile]
        Tests[pytest]
    end

    subgraph CI["🔄 CI / CD - GitHub Actions"]
        Lint[Lint pandera]
        TestCI[Tests automatiques]
        Build[Build Docker]
    end

    subgraph PROD["🌐 Production - Hébergement cloud"]
        ContainerApp[Container Streamlit]
        ContainerDB[Container PostgreSQL]
        ContainerAPI[Container Django REST]
        Storage[(Volume données Gold)]
    end

    Code --> CI
    Make --> Code
    Tests --> Code
    CI --> PROD
    ContainerApp <--> ContainerDB
    ContainerAPI <--> ContainerDB
    ContainerApp -.-> Storage
    ContainerDB -.-> Storage

    style PROD fill:#10b981,color:#fff
```
