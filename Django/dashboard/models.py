from django.db import models

class DimMedias(models.Model):
    media_id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=150, unique=True)
    media_type = models.CharField(max_length=10) # 'radio' ou 'tv'
    is_public_channel = models.BooleanField()
    media_group = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'dim_medias'
        managed = False


class DimTemps(models.Model):
    date_id = models.IntegerField(primary_key=True)
    date_pure = models.DateField(unique=True)
    annee = models.IntegerField()
    mois = models.IntegerField()
    jour = models.IntegerField()
    jour_semaine = models.CharField(max_length=15, blank=True, null=True)
    zone_vacances_scolaires = models.CharField(max_length=20, blank=True, null=True)
    est_jour_ferie = models.BooleanField(default=False)

    class Meta:
        db_table = 'dim_temps'
        managed = False


class DimThemesGenres(models.Model):
    categorie_id = models.AutoField(primary_key=True)
    nom_categorie = models.CharField(max_length=150, unique=True)
    type_categorie = models.CharField(max_length=50) # 'Theme JT' ou 'Genre Programme'

    class Meta:
        db_table = 'dim_themes_genres'
        managed = False


class FaitThemesDiffusion(models.Model):
    fait_theme_id = models.AutoField(primary_key=True)
    date = models.ForeignKey(DimTemps, models.DO_NOTHING, db_column='date_id')
    media = models.ForeignKey(DimMedias, models.DO_NOTHING, db_column='media_id')
    categorie = models.ForeignKey(DimThemesGenres, models.DO_NOTHING, db_column='categorie_id')
    nb_sujets = models.IntegerField(default=0)
    duree_sujets_secondes = models.IntegerField(default=0)

    class Meta:
        db_table = 'fait_themes_diffusion'
        managed = False


class FaitParoleAnalyseHoraire(models.Model):
    fait_parole_id = models.AutoField(primary_key=True)
    date = models.ForeignKey(DimTemps, models.DO_NOTHING, db_column='date_id')
    media = models.ForeignKey(DimMedias, models.DO_NOTHING, db_column='media_id')
    heure_diffusion = models.IntegerField()
    male_duration = models.IntegerField(default=0)
    female_duration = models.IntegerField(default=0)
    music_duration = models.IntegerField(default=0)

    class Meta:
        db_table = 'fait_parole_analyse_horaire'
        managed = False