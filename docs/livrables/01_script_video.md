# Script vidéo MVP — 15-20 minutes

## Cadre fixé par Sup de Vinci

- **Durée** : 15 à 20 minutes
- **Format** : screencast + voix off + caméra incrustée (optionnel mais recommandé)
- **Plan obligatoire** : besoin → solution → démo
- **Affichage obligatoire** : nom de chaque intervenant à l'écran quand il parle
- **Tous les membres** doivent prendre la parole
- **Format de sortie** : `.mp4` ou lien YouTube non répertoriée
- **Nommage** : `PE-2526_M1BDIA_NomPrenomEtudiant.mp4` *(à confirmer code promo)*

## Outils recommandés pour le tournage

- **OBS Studio** (gratuit, multi-plateforme) — capture écran + webcam + audio
- **Micro USB** type Blue Yeti, Rode NT-USB, ou Audio-Technica AT2020 — son propre (pas le micro de l'ordi)
- **Montage** : DaVinci Resolve (gratuit) ou CapCut PC
- **Templates d'incrustation nom** : titrage simple en bas de l'écran

## Préparation avant tournage

1. Lancer le dashboard en local et tester chaque page sans bug
2. Avoir les **diagrammes du `06_diagrammes.md`** prêts en SVG ou capturés en image (zoomables)
3. Préparer 3 « slides d'intro » : titre projet, équipe, plan
4. Préparer 1 « slide de clôture » : trouvailles + remerciements
5. Faire une lecture à blanc du script avec chronomètre (cible 17 minutes pour avoir du jeu)

---

# Script détaillé

Chaque section précise : **qui parle**, **ce qu'on voit à l'écran**, **ce qu'on dit**, **durée cible**.

---

## SECTION 1 — Ouverture et introduction (≈ 1 min 30)

**🎬 Visuel** : slide titre du projet + logo Sup de Vinci / Open Data University
**👤 Intervenant** : Lucas (incrustation : *Lucas [Nom] — Data & Frontend*)

> « Bonjour. Nous sommes [Lucas, Baptiste, Gérard], étudiants en Master 1 Big Data & IA à Sup de Vinci. Nous vous présentons aujourd'hui notre projet d'études, intitulé *"Les Français face à l'information"*. Ce projet est proposé par l'Open Data University, à partir des données publiques de l'INA, l'Institut national de l'audiovisuel. La consigne tient en deux phrases : analyser **vingt ans de journaux télévisés français** et la **représentation des femmes** dans l'audiovisuel. Dans les minutes qui viennent, nous allons vous expliquer pourquoi cette question compte, ce que nous avons construit pour y répondre, et ce que nous avons trouvé. »

**🎬 Transition** : fondu vers la slide « Plan de la présentation »

---

## SECTION 2 — Présentation de l'équipe (≈ 1 min)

**🎬 Visuel** : trois photos / avatars avec les noms et les rôles
**👤 Intervenants** : chacun se présente

**Lucas (incrustation : *Lucas [Nom] — Data & Frontend*)**
> « Sur ce projet, j'ai porté la partie données et frontend. J'ai construit le pipeline de nettoyage, les analyses statistiques, et le dashboard que vous allez voir tout à l'heure. »

**Baptiste (incrustation : *Baptiste [Nom] — Lead Backend*)**
> « De mon côté, j'ai conçu la base PostgreSQL, les modèles Django, et l'API qui exposera ces données. Mon objectif : que ce qu'on a construit puisse vivre au-delà de notre dashboard, et être consommé par d'autres applications. »

**Gérard (incrustation : *Gérard [Nom] — Data Quality & Documentation*)**
> « Et moi je me suis occupé de l'ingestion brute, des contrats de qualité avec pandera, des tests sur la base de données, et de la documentation utilisateur. Mon rôle : que tout ce qu'on livre soit reproductible et auditable. »

---

## SECTION 3 — Le besoin / la problématique (≈ 2 min)

**🎬 Visuel** : trois chiffres-chocs en fondu — *34 %*, *73 %*, *58 %*
**👤 Intervenant** : Lucas

> « Pourquoi ce sujet ? Trois chiffres résument l'enjeu. »

*Affichage du premier chiffre, 34 %*
> « En 2023, l'ARCOM, le régulateur français de l'audiovisuel, établit que les femmes ne représentent que **34 % du temps de parole** à la télévision et à la radio. »

*Affichage du deuxième chiffre, 73 %*
> « En 2013, *Le Monde* titrait qu'en dix ans, le nombre de faits divers dans les JT avait augmenté de **73 %**. »

*Affichage du troisième chiffre, 58 %*
> « Et en parallèle, **58 % des Français** s'informent désormais via les réseaux sociaux ou les plateformes vidéo au moins une fois par jour. La télé et la radio évoluent, mais elles continuent de structurer le débat public. »

**🎬 Visuel** : slide avec la question centrale du projet, mise en gras
> « **Notre question est simple : que regardent les Français à la télévision, par qui, et comment cela a-t-il évolué sur vingt ans ?** »

**🎬 Transition** : « Et surtout, notre apport original : **y a-t-il un lien entre la composition thématique d'une chaîne et la place qu'elle donne aux femmes à l'antenne ?** »

---

## SECTION 4 — La solution proposée — vue d'ensemble (≈ 2 min)

**🎬 Visuel** : diagramme architecture médaillon (depuis `06_diagrammes.md` § 1)
**👤 Intervenant** : Gérard

> « Pour répondre à cette question, nous avons construit un **pipeline data en quatre couches**, suivant le pattern *médaillon*. »

*Pointer chaque couche*
> « En entrée, sept jeux de données ouverts de l'INA. La couche **Bronze** ingère les CSV bruts et produit un rapport qualité automatique. La couche **Silver** nettoie, type, valide chaque table contre un contrat *pandera*, et déduplique. La couche **Gold** agrège tout cela en six tables analytiques prêtes à la visualisation. Enfin, la couche **consommation** alimente notre dashboard et, à terme, une API REST. »

**🎬 Transition (Baptiste)** : « En parallèle de la couche Gold en CSV, on a également chargé ces données dans une base **PostgreSQL** avec un schéma normalisé en 3NF. Cela permettra d'exposer les données via une API Django REST, et de brancher d'autres frontends que notre dashboard. »

**🎬 Transition (Lucas)** : « Sur les données Gold, on a appliqué trois techniques d'analyse avancée. »

---

## SECTION 5 — Les analyses avancées (≈ 2 min 30)

**🎬 Visuel** : slide « 3 analyses » avec icône PCA / k-means / PELT / Pearson
**👤 Intervenant** : Lucas

> « Premièrement, nous avons détecté automatiquement les **points de bascule** dans l'évolution mensuelle de chaque thème. On utilise l'algorithme **PELT** de la librairie *ruptures*. Concrètement : sur la rubrique Santé, on voit un saut brutal en mars 2020 — c'est l'arrivée du COVID. Sur la rubrique International, on voit des bascules autour des attentats de 2015. »

> « Deuxièmement, on a regroupé les chaînes en **trois archétypes** grâce à une **analyse en composantes principales (ACP)** suivie d'un **k-means**. Trois familles ressortent : les généralistes grand public, les chaînes internationales, et les newsrooms politiques. »

> « Troisièmement, et c'est le cœur de notre apport, nous avons calculé les **corrélations** entre chaque rubrique et le taux d'expression des femmes. Deux résultats forts : un coefficient de **−0,60 entre l'International et la parité**, et un coefficient de **+0,58 entre les Faits divers et la parité**. Autrement dit : plus une chaîne parle d'international, moins elle donne la parole aux femmes ; plus elle parle de proximité, plus la parité est respectée. »

---

## SECTION 6 — Démo du dashboard (≈ 7 min)

**🎬 Visuel** : capture écran live du dashboard Streamlit en plein écran
**👤 Intervenant** : Lucas (avec interventions courtes des deux autres aux moments-clés)

### 6.1 Page Accueil (≈ 1 min)

> « Voici le dashboard. La page d'accueil donne le pitch : 20 ans de JT, 25 ans de parité, 5 chaînes TV, plus de 280 000 sujets analysés. En dessous, **nos trois trouvailles majeures**. Et tout en bas, les sources et la méthodo. »

### 6.2 Page Agenda médiatique (≈ 1 min 30)

> « Ici, on regarde **ce dont parlent les JT**. L'onglet *Volumes* montre que TF1 et France 2 dominent en quantité de sujets diffusés. L'onglet *Thèmes* — c'est le plus parlant — montre l'évolution des grandes rubriques. Regardez : pic de Santé en 2020 — COVID. Politique France monte en flèche en 2007 et 2017 — élections présidentielles. »

> *(cliquer sur « Comment lire ce graphique ? »)*

> « Et pour chaque graphique, on a une explication accessible à tous, qui se déplie en un clic. C'est notre marque de fabrique : ce dashboard doit pouvoir être lu autant par un journaliste que par un proche qui n'a jamais fait de stats. »

### 6.3 Page Parité H/F (≈ 1 min 30)

> « Cette page montre la **représentation des femmes** à l'écran et à l'antenne. On peut basculer entre TV, Radio, et un mode Comparer. »

> *(basculer en mode Comparer)*

> « Le graphe montre une chose intéressante : la **radio a historiquement été en avance sur la parité**, et la TV rattrape. »

> *(basculer sur l'onglet Classement)*

> « Le classement annuel par chaîne. On voit que France Culture est régulièrement en tête, et BFM TV en bas. »

> *(basculer sur l'onglet Prime time)*

> « Et là, une question importante : la parité diffère-t-elle aux heures de grande écoute ? Réponse : oui, hors prime time est meilleur que prime time pour la TV — autrement dit, on voit moins de femmes aux heures où le plus de gens regardent. »

### 6.4 Page Thèmes × Parité — cœur du projet (≈ 2 min)

> « Voici la page qui répond à notre question centrale. »

> *(choisir la rubrique International)*

> « En abscisse, la part du temps qu'une chaîne consacre à l'International. En ordonnée, le taux d'expression des femmes. Chaque point est une chaîne sur une année. La ligne descendante de la régression dit clairement : **plus on parle d'international, moins les femmes prennent la parole**. »

> *(basculer sur l'onglet Matrice)*

> « Vue globale : la barre rouge en bas, c'est International, le plus négativement corrélé. Les barres vertes en haut, ce sont Faits divers et Sciences — les plus positivement corrélés. »

### 6.5 Page Analyses avancées (≈ 1 min)

> « Dernière page, plus technique. Le clustering ACP montre les trois archétypes que je mentionnais. Et la détection de ruptures, je vais prendre la rubrique Santé... »

> *(sélectionner Santé)*

> « Les diamants rouges, ce sont les ruptures détectées automatiquement. On en voit une très nette à partir de 2020 — l'algorithme a identifié seul l'arrivée du COVID, sans qu'on lui dise quoi chercher. »

---

## SECTION 7 — Aspect backend (≈ 1 min 30)

**🎬 Visuel** : diagramme ER de la BDD + capture de Django Admin (si dispo)
**👤 Intervenant** : Baptiste

> « En complément du dashboard, j'ai construit la couche backend. Voici le schéma de la base PostgreSQL : 5 tables normalisées, 268 000 lignes pour les stats quotidiennes, des index optimisés et des vues matérialisées pour les agrégats fréquents. »

> « Côté Django, on a les modèles ORM avec validators et properties calculées. L'API REST exposera bientôt les endpoints `/api/channels/`, `/api/themes/`, `/api/daily-stats/`, `/api/analytics/`. L'idée : permettre à des frontends tiers — un site web public, une application mobile — de consommer ces données. »

---

## SECTION 8 — Méthodologie et organisation (≈ 1 min)

**🎬 Visuel** : Gantt depuis `00_planning.md`
**👤 Intervenant** : Gérard

> « Côté organisation : 5 mois de février à juin, méthodologie agile, sprints de 2 semaines, code review systématique, et un point synchro deux fois par semaine. La répartition des rôles vous a été présentée. »

> « Sur la qualité : on a **douze contrats *pandera*** actifs — un par table produite — qui vérifient les types, les bornes, les valeurs autorisées. Par défaut on log un warning quand un contrat échoue, et on peut activer un mode strict pour la CI qui bloque le pipeline. Sortie type : douze lignes ✓ dans le log. Le pipeline complet se rejoue en quelques minutes avec `make pipeline && make analyses && make dashboard`. Un nouveau membre peut lancer le projet en moins d'une heure avec la doc qu'on a écrite. »

---

## SECTION 9 — Conclusion et perspectives (≈ 1 min)

**🎬 Visuel** : slide « Trouvailles » + « Perspectives »
**👤 Intervenants** : chacun conclut sur son volet

**Lucas**
> « Sur les **données** : on a démontré qu'il existe un lien statistiquement fort entre l'agenda éditorial d'une chaîne et la parité H/F. Cette trouvaille n'était pas attendue dans le défi, c'est notre apport propre. »

**Baptiste**
> « Sur la **technique** : le backend va permettre d'ouvrir ces données via API. À terme, on souhaite déployer le tout sur Streamlit Cloud et Railway, et publier une réutilisation sur data.gouv.fr. »

**Gérard**
> « Et sur la **qualité** : le projet est reproductible, documenté, validé schéma par schéma. Il peut vivre au-delà de notre rendu. »

**Lucas (clôture)**
> « Merci pour votre attention. Le code est sur GitHub, la documentation complète est dans le dossier `docs/`. Nous restons à votre disposition pour toute question. »

**🎬 Visuel final** : carte de remerciement + URL du repo + adresses email équipe

---

# Checklist avant tournage

- [ ] Dashboard testé sur les 5 pages, aucun bug
- [ ] Pipeline rejoué la veille pour vérifier que les données sont à jour
- [ ] Slides intro / clôture créées (titre, plan, équipe, trouvailles, merci)
- [ ] Diagrammes Mermaid exportés en SVG ou PNG haute résolution
- [ ] Captures d'écran de Django Admin si dispo (sinon : sauter sur la matrice ER)
- [ ] Micros testés sur les 3 voix
- [ ] Test de prise vidéo de 30 secondes pour caler les niveaux audio
- [ ] Tour de table : chacun connaît son passage (lire le script à blanc une fois)
- [ ] Si tournage en plusieurs prises : marquer un clap visuel pour le montage
- [ ] Vérifier la nomenclature du fichier de sortie avant d'envoyer
