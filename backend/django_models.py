"""
Django Models pour le projet Audiovisuel INA
Open Data University - Lassitude

Usage:
    1. Copier ce fichier dans votre app Django (models.py)
    2. Configurer settings.py avec PostgreSQL
    3. Exécuter: python manage.py makemigrations
    4. Exécuter: python manage.py migrate
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Channel(models.Model):
    """Chaîne TV ou station radio"""
    
    MEDIA_TYPE_CHOICES = [
        ('tv', 'Télévision'),
        ('radio', 'Radio'),
    ]
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Nom de la chaîne"
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name="Chaîne publique"
    )
    media_type = models.CharField(
        max_length=10, 
        choices=MEDIA_TYPE_CHOICES,
        verbose_name="Type de média"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'channels'
        verbose_name = 'Chaîne'
        verbose_name_plural = 'Chaînes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def type_display(self):
        """Retourne le type de média en français"""
        return "Publique" if self.is_public else "Privée"


class Theme(models.Model):
    """Thème/rubrique des sujets"""
    
    CATEGORY_CHOICES = [
        ('information', 'Information'),
        ('culture', 'Culture'),
        ('sport', 'Sport'),
        ('divertissement', 'Divertissement'),
    ]
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Nom du thème"
    )
    slug = models.SlugField(
        max_length=100, 
        unique=True,
        verbose_name="Slug"
    )
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Catégorie"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description"
    )
    color_hex = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Code couleur hexadécimal (ex: #FF5733)",
        verbose_name="Couleur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes'
        verbose_name = 'Thème'
        verbose_name_plural = 'Thèmes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le slug si non fourni"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DailyStat(models.Model):
    """Statistiques quotidiennes des JT"""
    
    date = models.DateField(verbose_name="Date")
    channel = models.ForeignKey(
        Channel, 
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name="Chaîne"
    )
    theme = models.ForeignKey(
        Theme, 
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name="Thème"
    )
    nb_subjects = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Nombre de sujets"
    )
    duration_sec = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Durée (secondes)"
    )
    
    # Features calculées
    avg_duration_per_subject = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Durée moyenne/sujet"
    )
    day_of_week = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Jour de la semaine"
    )
    week_number = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(53)],
        verbose_name="Numéro de semaine"
    )
    month = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Mois"
    )
    quarter = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Trimestre"
    )
    year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Année"
    )
    is_weekend = models.BooleanField(
        default=False,
        verbose_name="Weekend"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_stats'
        verbose_name = 'Statistique quotidienne'
        verbose_name_plural = 'Statistiques quotidiennes'
        ordering = ['-date', 'channel', 'theme']
        unique_together = [['date', 'channel', 'theme']]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['channel']),
            models.Index(fields=['theme']),
            models.Index(fields=['year', 'month']),
            models.Index(fields=['date', 'channel']),
            models.Index(fields=['date', 'theme']),
            models.Index(fields=['channel', 'theme', 'date']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.channel.name} - {self.theme.name}"
    
    @property
    def duration_minutes(self):
        """Retourne la durée en minutes"""
        return round(self.duration_sec / 60, 2)
    
    @property
    def duration_hours(self):
        """Retourne la durée en heures"""
        return round(self.duration_sec / 3600, 2)
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement avg_duration_per_subject"""
        if self.nb_subjects > 0:
            self.avg_duration_per_subject = self.duration_sec / self.nb_subjects
        else:
            self.avg_duration_per_subject = 0
        super().save(*args, **kwargs)


class YearlyGender(models.Model):
    """Taux d'expression femmes/hommes par année"""
    
    channel = models.ForeignKey(
        Channel, 
        on_delete=models.CASCADE,
        related_name='yearly_gender',
        verbose_name="Chaîne"
    )
    year = models.IntegerField(verbose_name="Année")
    women_expression_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pourcentage de temps de parole féminine",
        verbose_name="Taux expression femmes (%)"
    )
    speech_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taux de parole vs musique",
        verbose_name="Taux de parole (%)"
    )
    nb_hours_analyzed = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Heures analysées"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'yearly_gender'
        verbose_name = 'Statistique genre annuelle'
        verbose_name_plural = 'Statistiques genre annuelles'
        ordering = ['-year', 'channel']
        unique_together = [['channel', 'year']]
        indexes = [
            models.Index(fields=['channel']),
            models.Index(fields=['year']),
        ]
    
    def __str__(self):
        return f"{self.year} - {self.channel.name}"
    
    @property
    def men_expression_rate(self):
        """Calcule le taux d'expression masculine"""
        if self.women_expression_rate:
            return 100 - self.women_expression_rate
        return None


class HourlyStat(models.Model):
    """Statistiques horaires du temps de parole"""
    
    channel = models.ForeignKey(
        Channel, 
        on_delete=models.CASCADE,
        related_name='hourly_stats',
        verbose_name="Chaîne"
    )
    date = models.DateField(verbose_name="Date")
    hour = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        verbose_name="Heure"
    )
    male_duration = models.IntegerField(
        default=0,
        help_text="Durée de parole masculine en secondes",
        verbose_name="Durée parole masculine (s)"
    )
    female_duration = models.IntegerField(
        default=0,
        help_text="Durée de parole féminine en secondes",
        verbose_name="Durée parole féminine (s)"
    )
    music_duration = models.IntegerField(
        default=0,
        help_text="Durée de musique en secondes",
        verbose_name="Durée musique (s)"
    )
    is_holiday = models.BooleanField(
        default=False,
        verbose_name="Jour férié"
    )
    holiday_zones = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Zones en vacances (A, B, C)",
        verbose_name="Zones vacances"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hourly_stats'
        verbose_name = 'Statistique horaire'
        verbose_name_plural = 'Statistiques horaires'
        ordering = ['-date', 'hour']
        unique_together = [['channel', 'date', 'hour']]
        indexes = [
            models.Index(fields=['channel']),
            models.Index(fields=['date']),
            models.Index(fields=['hour']),
            models.Index(fields=['channel', 'date', 'hour']),
        ]
    
    def __str__(self):
        return f"{self.date} {self.hour}h - {self.channel.name}"
    
    @property
    def total_speech_duration(self):
        """Durée totale de parole (hommes + femmes)"""
        return self.male_duration + self.female_duration
    
    @property
    def women_percentage(self):
        """Pourcentage de parole féminine"""
        total = self.total_speech_duration
        if total > 0:
            return round((self.female_duration / total) * 100, 2)
        return 0
    
    @property
    def men_percentage(self):
        """Pourcentage de parole masculine"""
        total = self.total_speech_duration
        if total > 0:
            return round((self.male_duration / total) * 100, 2)
        return 0


# ============================================================================
# MANAGERS PERSONNALISÉS (Optionnel mais utile)
# ============================================================================

class DailyStatManager(models.Manager):
    """Manager personnalisé pour DailyStat"""
    
    def by_theme(self, theme):
        """Filtre par thème"""
        return self.filter(theme=theme)
    
    def by_channel(self, channel):
        """Filtre par chaîne"""
        return self.filter(channel=channel)
    
    def by_year(self, year):
        """Filtre par année"""
        return self.filter(year=year)
    
    def by_date_range(self, start_date, end_date):
        """Filtre par plage de dates"""
        return self.filter(date__gte=start_date, date__lte=end_date)
    
    def top_themes(self, limit=10):
        """Retourne les thèmes les plus diffusés"""
        from django.db.models import Sum
        return (self.values('theme__name')
                .annotate(total_subjects=Sum('nb_subjects'))
                .order_by('-total_subjects')[:limit])


# Ajouter le manager personnalisé (optionnel)
# DailyStat.objects = DailyStatManager()
