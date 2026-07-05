-- ============================================================================
-- SCHÉMA BDD POSTGRESQL - PROJET AUDIOVISUEL INA
-- Open Data University - Lassitude
-- ============================================================================

-- Supprimer les tables existantes si besoin (DEV only)
DROP TABLE IF EXISTS hourly_stats CASCADE;
DROP TABLE IF EXISTS yearly_gender CASCADE;
DROP TABLE IF EXISTS daily_stats CASCADE;
DROP TABLE IF EXISTS themes CASCADE;
DROP TABLE IF EXISTS channels CASCADE;

-- ============================================================================
-- TABLE: channels
-- Description: Référentiel des chaînes TV et stations radio
-- ============================================================================
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_public BOOLEAN DEFAULT TRUE,
    media_type VARCHAR(10) CHECK (media_type IN ('tv', 'radio')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherches fréquentes
CREATE INDEX idx_channels_media_type ON channels(media_type);
CREATE INDEX idx_channels_is_public ON channels(is_public);

-- Commentaires
COMMENT ON TABLE channels IS 'Référentiel des chaînes TV et stations radio';
COMMENT ON COLUMN channels.name IS 'Nom de la chaîne (TF1, France 2, etc.)';
COMMENT ON COLUMN channels.is_public IS 'Chaîne publique (true) ou privée (false)';
COMMENT ON COLUMN channels.media_type IS 'Type de média: tv ou radio';

-- ============================================================================
-- TABLE: themes
-- Description: Référentiel des thèmes/rubriques
-- ============================================================================
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    color_hex VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherches
CREATE INDEX idx_themes_category ON themes(category);
CREATE INDEX idx_themes_slug ON themes(slug);

-- Commentaires
COMMENT ON TABLE themes IS 'Référentiel des thèmes et rubriques des JT';
COMMENT ON COLUMN themes.name IS 'Nom du thème (ex: Société, International)';
COMMENT ON COLUMN themes.slug IS 'Slug pour URLs (ex: societe, international)';
COMMENT ON COLUMN themes.category IS 'Catégorie parent (Info, Culture, Sport)';
COMMENT ON COLUMN themes.color_hex IS 'Couleur hex pour visualisations (#FF5733)';

-- ============================================================================
-- TABLE: daily_stats
-- Description: Statistiques quotidiennes par chaîne et thème
-- ============================================================================
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    nb_subjects INTEGER NOT NULL DEFAULT 0,
    duration_sec INTEGER NOT NULL DEFAULT 0,
    
    -- Features calculées
    avg_duration_per_subject NUMERIC(10,2),
    day_of_week VARCHAR(10),
    week_number INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contrainte d'unicité
    UNIQUE(date, channel_id, theme_id)
);

-- Index optimisés pour les requêtes temporelles
CREATE INDEX idx_daily_stats_date ON daily_stats(date);
CREATE INDEX idx_daily_stats_channel ON daily_stats(channel_id);
CREATE INDEX idx_daily_stats_theme ON daily_stats(theme_id);
CREATE INDEX idx_daily_stats_year_month ON daily_stats(year, month);
CREATE INDEX idx_daily_stats_date_channel ON daily_stats(date, channel_id);
CREATE INDEX idx_daily_stats_date_theme ON daily_stats(date, theme_id);

-- Index composite pour performances
CREATE INDEX idx_daily_stats_composite ON daily_stats(channel_id, theme_id, date);

-- Commentaires
COMMENT ON TABLE daily_stats IS 'Statistiques quotidiennes des JT par chaîne et thème';
COMMENT ON COLUMN daily_stats.nb_subjects IS 'Nombre de sujets diffusés';
COMMENT ON COLUMN daily_stats.duration_sec IS 'Durée totale en secondes';
COMMENT ON COLUMN daily_stats.avg_duration_per_subject IS 'Durée moyenne par sujet (calculée)';

-- ============================================================================
-- TABLE: yearly_gender
-- Description: Taux d'expression femmes/hommes par année et chaîne
-- ============================================================================
CREATE TABLE yearly_gender (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    women_expression_rate NUMERIC(5,2),
    speech_rate NUMERIC(5,2),
    nb_hours_analyzed INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contrainte d'unicité
    UNIQUE(channel_id, year)
);

-- Index
CREATE INDEX idx_yearly_gender_channel ON yearly_gender(channel_id);
CREATE INDEX idx_yearly_gender_year ON yearly_gender(year);

-- Commentaires
COMMENT ON TABLE yearly_gender IS 'Taux d''expression des femmes par année et chaîne';
COMMENT ON COLUMN yearly_gender.women_expression_rate IS 'Pourcentage de parole féminine';
COMMENT ON COLUMN yearly_gender.speech_rate IS 'Taux de parole (vs musique)';
COMMENT ON COLUMN yearly_gender.nb_hours_analyzed IS 'Nombre d''heures analysées';

-- ============================================================================
-- TABLE: hourly_stats
-- Description: Statistiques horaires de parole (gender data)
-- ============================================================================
CREATE TABLE hourly_stats (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    male_duration INTEGER DEFAULT 0,
    female_duration INTEGER DEFAULT 0,
    music_duration INTEGER DEFAULT 0,
    is_holiday BOOLEAN DEFAULT FALSE,
    holiday_zones VARCHAR(10),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contrainte d'unicité
    UNIQUE(channel_id, date, hour)
);

-- Index
CREATE INDEX idx_hourly_stats_channel ON hourly_stats(channel_id);
CREATE INDEX idx_hourly_stats_date ON hourly_stats(date);
CREATE INDEX idx_hourly_stats_hour ON hourly_stats(hour);
CREATE INDEX idx_hourly_stats_composite ON hourly_stats(channel_id, date, hour);

-- Commentaires
COMMENT ON TABLE hourly_stats IS 'Statistiques horaires du temps de parole par genre';
COMMENT ON COLUMN hourly_stats.male_duration IS 'Durée de parole masculine (secondes)';
COMMENT ON COLUMN hourly_stats.female_duration IS 'Durée de parole féminine (secondes)';
COMMENT ON COLUMN hourly_stats.music_duration IS 'Durée de musique (secondes)';
COMMENT ON COLUMN hourly_stats.holiday_zones IS 'Zones en vacances (A, B, C)';

-- ============================================================================
-- VUES MATÉRIALISÉES POUR PERFORMANCES
-- ============================================================================

-- Vue: Stats agrégées par thème et année
CREATE MATERIALIZED VIEW mv_theme_yearly_stats AS
SELECT 
    t.id as theme_id,
    t.name as theme_name,
    ds.year,
    SUM(ds.nb_subjects) as total_subjects,
    SUM(ds.duration_sec) as total_duration_sec,
    AVG(ds.avg_duration_per_subject) as avg_duration_per_subject,
    COUNT(DISTINCT ds.channel_id) as nb_channels,
    COUNT(DISTINCT ds.date) as nb_days
FROM daily_stats ds
JOIN themes t ON ds.theme_id = t.id
GROUP BY t.id, t.name, ds.year;

CREATE INDEX idx_mv_theme_yearly_theme ON mv_theme_yearly_stats(theme_id);
CREATE INDEX idx_mv_theme_yearly_year ON mv_theme_yearly_stats(year);

-- Vue: Stats agrégées par chaîne et année
CREATE MATERIALIZED VIEW mv_channel_yearly_stats AS
SELECT 
    c.id as channel_id,
    c.name as channel_name,
    ds.year,
    SUM(ds.nb_subjects) as total_subjects,
    SUM(ds.duration_sec) as total_duration_sec,
    AVG(ds.avg_duration_per_subject) as avg_duration_per_subject,
    COUNT(DISTINCT ds.theme_id) as nb_themes,
    COUNT(DISTINCT ds.date) as nb_days
FROM daily_stats ds
JOIN channels c ON ds.channel_id = c.id
GROUP BY c.id, c.name, ds.year;

CREATE INDEX idx_mv_channel_yearly_channel ON mv_channel_yearly_stats(channel_id);
CREATE INDEX idx_mv_channel_yearly_year ON mv_channel_yearly_stats(year);

-- ============================================================================
-- FONCTIONS UTILITAIRES
-- ============================================================================

-- Fonction: Rafraîchir toutes les vues matérialisées
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_theme_yearly_stats;
    REFRESH MATERIALIZED VIEW mv_channel_yearly_stats;
END;
$$ LANGUAGE plpgsql;

-- Fonction: Calculer la durée moyenne par sujet
CREATE OR REPLACE FUNCTION calculate_avg_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.nb_subjects > 0 THEN
        NEW.avg_duration_per_subject := NEW.duration_sec::NUMERIC / NEW.nb_subjects;
    ELSE
        NEW.avg_duration_per_subject := 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Calculer automatiquement avg_duration_per_subject
CREATE TRIGGER trg_calculate_avg_duration
BEFORE INSERT OR UPDATE ON daily_stats
FOR EACH ROW
EXECUTE FUNCTION calculate_avg_duration();

-- Fonction: Mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at sur toutes les tables
CREATE TRIGGER trg_channels_updated_at
BEFORE UPDATE ON channels
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_themes_updated_at
BEFORE UPDATE ON themes
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_daily_stats_updated_at
BEFORE UPDATE ON daily_stats
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_yearly_gender_updated_at
BEFORE UPDATE ON yearly_gender
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_hourly_stats_updated_at
BEFORE UPDATE ON hourly_stats
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- DONNÉES INITIALES - CHAÎNES TV
-- ============================================================================
INSERT INTO channels (name, is_public, media_type) VALUES
('TF1', false, 'tv'),
('France 2', true, 'tv'),
('France 3', true, 'tv'),
('M6', false, 'tv'),
('Arte', true, 'tv');

-- ============================================================================
-- DONNÉES INITIALES - THÈMES
-- ============================================================================
INSERT INTO themes (name, slug, category, color_hex) VALUES
('Société', 'societe', 'Information', '#2E86AB'),
('International', 'international', 'Information', '#A23B72'),
('Politique France', 'politique-france', 'Information', '#F18F01'),
('Economie', 'economie', 'Information', '#C73E1D'),
('Culture-loisirs', 'culture-loisirs', 'Culture', '#6A4C93'),
('Sport', 'sport', 'Sport', '#06A77D'),
('Catastrophes', 'catastrophes', 'Information', '#D62828'),
('Justice', 'justice', 'Information', '#003049'),
('Santé', 'sante', 'Information', '#F77F00'),
('Environnement', 'environnement', 'Information', '#06D6A0'),
('Faits divers', 'faits-divers', 'Information', '#EF476F'),
('Histoire-hommages', 'histoire-hommages', 'Culture', '#118AB2'),
('Sciences et techniques', 'sciences-techniques', 'Culture', '#073B4C'),
('Education', 'education', 'Information', '#FFD166');

-- ============================================================================
-- REQUÊTES UTILES POUR VÉRIFICATION
-- ============================================================================

-- Compter les enregistrements par table
-- SELECT 'channels' as table_name, COUNT(*) as count FROM channels
-- UNION ALL
-- SELECT 'themes', COUNT(*) FROM themes
-- UNION ALL
-- SELECT 'daily_stats', COUNT(*) FROM daily_stats
-- UNION ALL
-- SELECT 'yearly_gender', COUNT(*) FROM yearly_gender
-- UNION ALL
-- SELECT 'hourly_stats', COUNT(*) FROM hourly_stats;

-- Vérifier les index
-- SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;

-- Taille des tables
-- SELECT 
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- FIN DU SCHÉMA
-- ============================================================================
