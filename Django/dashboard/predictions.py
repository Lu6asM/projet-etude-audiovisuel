import pandas as pd
import numpy as np
from django.db import models
from sklearn.linear_model import LinearRegression
from .models import FaitParoleAnalyseHoraire, FaitThemesDiffusion

def predire_evolution_parole():
    """Prédit le taux de parole des femmes pour les années à venir avec une tendance."""
    raw_data = FaitParoleAnalyseHoraire.objects.values('date__annee').annotate(
        f=models.Sum('female_duration'),
        m=models.Sum('male_duration')
    ).order_by('date__annee')

    df = pd.DataFrame(list(raw_data))
    if df.empty:
        return {'labels': [], 'historique': [], 'predictions': []}

    df['taux_femmes'] = (df['f'] / (df['f'] + df['m'])) * 100

    X = df[['date__annee']].values
    y = df['taux_femmes'].values

    # Régression Linéaire
    model = LinearRegression()
    model.fit(X, y)

    dernier_an = int(X.max())
    annees_futures = np.array([[an] for an in range(dernier_an + 1, 2031)])
    predictions_futures = model.predict(annees_futures)

    # Pour Chart.js
    labels = list(df['date__annee']) + [int(an[0]) for an in annees_futures]
    historique = list(df['taux_femmes']) + [None] * len(annees_futures)
    predictions = [None] * (len(df) - 1) + [df['taux_femmes'].iloc[-1]] + list(predictions_futures)

    return {
        'labels': labels,
        'historique': [round(x, 2) if x is not None else None for x in historique],
        'predictions': [round(x, 2) if x is not None else None for x in predictions]
    }