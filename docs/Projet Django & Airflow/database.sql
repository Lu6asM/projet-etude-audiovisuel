-- Dimensions
CREATE TABLE dim_medias (
    media_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(150) NOT NULL UNIQUE,
    media_type VARCHAR(10) CHECK (media_type IN ('radio', 'tv')),
    is_public_channel BOOLEAN NOT NULL,
    media_group VARCHAR(150) 
);

CREATE TABLE dim_temps (
    date_id INT PRIMARY KEY, -- Format YYYYMMDD 20201226
    date_pure DATE NOT NULL UNIQUE, 
    annee INT NOT NULL,
    mois INT NOT NULL,
    jour INT NOT NULL,
    jour_semaine VARCHAR(15), 
    zone_vacances_scolaires VARCHAR(20), 
    est_jour_ferie BOOLEAN DEFAULT FALSE
);

CREATE TABLE dim_themes_genres (
    categorie_id SERIAL PRIMARY KEY,
    nom_categorie VARCHAR(150) NOT NULL UNIQUE, 
    type_categorie VARCHAR(50) CHECK (type_categorie IN ('Theme JT', 'Genre Programme'))
);


-- Faits
-- Évolution des thèmes
CREATE TABLE fait_themes_diffusion (
    fait_theme_id SERIAL PRIMARY KEY,
    date_id INT REFERENCES dim_temps(date_id),
    media_id INT REFERENCES dim_medias(media_id),
    categorie_id INT REFERENCES dim_themes_genres(categorie_id),
    nb_sujets INT DEFAULT 0,
    duree_sujets_secondes INT DEFAULT 0
);

-- horaire du temps de parole
CREATE TABLE fait_parole_analyse_horaire (
    fait_parole_id SERIAL PRIMARY KEY,
    date_id INT REFERENCES dim_temps(date_id),
    media_id INT REFERENCES dim_medias(media_id),
    heure_diffusion INT CHECK (heure_diffusion BETWEEN 0 AND 23),
    male_duration INT DEFAULT 0,   
    female_duration INT DEFAULT 0,  
    music_duration INT DEFAULT 0    
);

--Synthèse annuelle par genre de programme
CREATE TABLE fait_parole_annuelle_genre (
    fait_synthese_id SERIAL PRIMARY KEY,
    annee INT NOT NULL,
    categorie_id INT REFERENCES dim_themes_genres(categorie_id),
    nb_declarations INT DEFAULT 0,
    total_declarations_duration NUMERIC(15, 2) DEFAULT 0.0,
    women_speech_duration NUMERIC(15, 2) DEFAULT 0.0,
    men_speech_duration NUMERIC(15, 2) DEFAULT 0.0,
    other_duration NUMERIC(15, 2) DEFAULT 0.0
);


-- Index
CREATE INDEX idx_fait_theme_date ON fait_themes_diffusion(date_id);
CREATE INDEX idx_fait_theme_media ON fait_themes_diffusion(media_id);

CREATE INDEX idx_fait_parole_date ON fait_parole_analyse_horaire(date_id);
CREATE INDEX idx_fait_parole_media ON fait_parole_analyse_horaire(media_id);
CREATE INDEX idx_fait_parole_heure ON fait_parole_analyse_horaire(heure_diffusion);


-- Taux de parole des femmes
CREATE OR REPLACE VIEW vue_taux_parole_femmes_horaire AS
SELECT 
    t.annee,
    t.jour_semaine,
    m.channel_name,
    m.media_type,
    m.is_public_channel,
    f.heure_diffusion,
    SUM(f.female_duration) as total_femmes_sec,
    SUM(f.male_duration) as total_hommes_sec,
    CASE 
        WHEN (SUM(f.female_duration) + SUM(f.male_duration)) > 0 
        THEN ROUND((SUM(f.female_duration)::NUMERIC / (SUM(f.female_duration) + SUM(f.male_duration))::NUMERIC) * 100, 2)
        ELSE 0
    END as taux_expression_femmes_pourcent
FROM fait_parole_analyse_horaire f
JOIN dim_temps t ON f.date_id = t.date_id
JOIN dim_medias m ON f.media_id = m.media_id
GROUP BY t.annee, t.jour_semaine, m.channel_name, m.media_type, m.is_public_channel, f.heure_diffusion;







INSERT INTO dim_temps (date_id, date_pure, jour, mois, annee, jour_semaine)
SELECT 
    to_char(datum, 'YYYYMMDD')::integer AS date_id,
    datum AS date_complete,
    extract(day FROM datum) AS jour,
    extract(month FROM datum) AS mois,
    extract(year FROM datum) AS annee,
    extract(isodow FROM datum) AS jour_semaine
FROM generate_series('2000-01-01'::date, '2030-12-31'::date, '1 day'::interval) datum
ON CONFLICT (date_id) DO NOTHING;




INSERT INTO dim_temps (date_id, date_pure, jour, mois, annee, jour_semaine)
SELECT 
    to_char(datum, 'YYYYMMDD')::integer AS date_id,
    datum AS date_complete,
    extract(day FROM datum) AS jour,
    extract(month FROM datum) AS mois,
    extract(year FROM datum) AS annee,
    extract(isodow FROM datum) AS jour_semaine
FROM generate_series('1995-01-01'::date, '2030-12-31'::date, '1 day'::interval) datum -- <-- Changement ici
ON CONFLICT (date_id) DO NOTHING;