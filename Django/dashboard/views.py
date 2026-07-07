from django.shortcuts import render
from django.db.models import Sum, Avg, F
from django.db.models.functions import Cast
from django.db.models import FloatField, Sum, Case, When, Value, CharField
from .models import FaitThemesDiffusion, FaitParoleAnalyseHoraire, DimMedias, DimThemesGenres
from .predictions import predire_evolution_parole
from django.http import JsonResponse

# Template principal
def dashboard_view(request):
    return render(request, 'index.html')

# Évolution du temps de parole par année
def data_temps_parole(request):
    donnees = (
        FaitParoleAnalyseHoraire.objects
        .values('date__annee')
        .annotate(
            total_femmes=Sum('female_duration'),
            total_hommes=Sum('male_duration')
        )
        .order_by('date__annee')
    )

    categories_ans = [item['date__annee'] for item in donnees]
    data_femmes = [round(item['total_femmes'] / 3600, 2) for item in donnees]
    data_hommes = [round(item['total_hommes'] / 3600, 2) for item in donnees]

    return JsonResponse({
        'labels': categories_ans,
        'femmes': data_femmes,
        'hommes': data_hommes
    })

def data_themes_evolution(request):
    donnees = (
        FaitThemesDiffusion.objects
        .values('categorie__nom_categorie')
        .annotate(total_sujets=Sum('nb_sujets'))
        .order_by('-total_sujets')[:10] # Top 10
    )

    labels = [item['categorie__nom_categorie'] for item in donnees]
    values = [item['total_sujets'] for item in donnees]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


# Les pages
def page_themes_jt(request):
    return render(request, 'page_themes_jt.html')


def page_parole_global(request):
    return render(request, 'page_parole_global.html')


def page_parole_zoom(request):
    return render(request, 'page_parole_zoom.html')


# APPELS APIs
def api_themes_jt(request):
    top_themes = FaitThemesDiffusion.objects.values('categorie__nom_categorie').annotate(
        total=Sum('nb_sujets')).order_by('-total')[:5]

    evol_faits_divers = FaitThemesDiffusion.objects.filter(categorie__nom_categorie__icontains="catastrophe").values(
        'date__annee').annotate(total=Sum('nb_sujets')).order_by('date__annee')

    duree_moyenne = FaitThemesDiffusion.objects.values('categorie__nom_categorie').annotate(
        moyenne=Cast(Sum('duree_sujets_secondes'), FloatField()) / Cast(Sum('nb_sujets'), FloatField())
    ).order_by('-moyenne')

    parts_medias = FaitThemesDiffusion.objects.values('media__is_public_channel').annotate(total=Sum('nb_sujets'))

    return JsonResponse({
        'g1': {'labels': [x['categorie__nom_categorie'] for x in top_themes],
               'values': [x['total'] for x in top_themes]},
        'g2': {'labels': [x['date__annee'] for x in evol_faits_divers],
               'values': [x['total'] for x in evol_faits_divers]},
        'g3': {'labels': [x['categorie__nom_categorie'] for x in duree_moyenne],
               'values': [round(x['moyenne'], 1) for x in duree_moyenne]},
        'g4': {'labels': ['Public', 'Privé'], 'values': [x['total'] for x in parts_medias]}
    })


def api_parole_global(request):
    evol_globale = FaitParoleAnalyseHoraire.objects.values('date__annee').annotate(f=Sum('female_duration'),
                                                                                   m=Sum('male_duration')).order_by(
        'date__annee')

    media_split = FaitParoleAnalyseHoraire.objects.values('media__media_type').annotate(f=Sum('female_duration'),
                                                                                        m=Sum('male_duration'))

    musique_evol = FaitParoleAnalyseHoraire.objects.values('date__annee').annotate(musique=Sum('music_duration'),
                                                                                   parole=Sum('female_duration') + Sum(
                                                                                       'male_duration')).order_by(
        'date__annee')

    top_annees = evol_globale[:5]

    return JsonResponse({
        'g1': {
            'labels': [x['date__annee'] for x in evol_globale],
            'femmes': [round(x['f'] / 3600, 1) for x in evol_globale],
            'hommes': [round(x['m'] / 3600, 1) for x in evol_globale]
        },
        'g2': {
            'labels': [x['media__media_type'] for x in media_split],
            'femmes': [x['f'] for x in media_split],
            'hommes': [x['m'] for x in media_split]
        },
        'g3': {
            'labels': [x['date__annee'] for x in musique_evol],
            'musique': [round(x['musique'] / 3600, 1) for x in musique_evol],
            'parole': [round(x['parole'] / 3600, 1) for x in musique_evol]
        },
        'g4': {
            'labels': [x['date__annee'] for x in top_annees],
            'taux': [round((x['f'] / (x['f'] + x['m'])) * 100, 2) if (x['f'] + x['m']) > 0 else 0 for x in top_annees]
        }
    })

def calculer_taux(periode_name, data_periode):
    donnees = data_periode.get(periode_name)
    if not donnees:
        return 0
    total = donnees['f'] + donnees['m']
    return round((donnees['f'] / total) * 100, 1) if total > 0 else 0


def api_parole_zoom(request):
    par_heure = FaitParoleAnalyseHoraire.objects.values('heure_diffusion').annotate(f=Sum('female_duration'),
                                                                                    m=Sum('male_duration')).order_by(
        'heure_diffusion')

    top_chaines = FaitParoleAnalyseHoraire.objects.values('media__channel_name').annotate(f=Sum('female_duration'),
                                                                                          m=Sum('male_duration'))

    public_priv = FaitParoleAnalyseHoraire.objects.values('media__is_public_channel').annotate(f=Sum('female_duration'),
                                                                                               m=Sum('male_duration'))

    nuit_vs_jour = FaitParoleAnalyseHoraire.objects.values('heure_diffusion').annotate(f=Sum('female_duration'),
                                                                                       m=Sum('male_duration'))
    nuit_vs_jour_queryset = FaitParoleAnalyseHoraire.objects.annotate(
        periode=Case(
            When(heure_diffusion__gte=0, heure_diffusion__lt=6, then=Value('Nuit')),
            default=Value('Jour'),
            output_field=CharField(),
        )
    ).values('periode').annotate(
        f=Sum('female_duration'),
        m=Sum('male_duration')
    )

    data_periode = {item['periode']: item for item in nuit_vs_jour_queryset}

    taux_nuit = calculer_taux('Nuit', data_periode)
    taux_jour = calculer_taux('Jour', data_periode)
    return JsonResponse({
        'g1': {
            'labels': [f"{x['heure_diffusion']}h" for x in par_heure],
            'taux': [round((x['f'] / (x['f'] + x['m'])) * 100, 1) if (x['f'] + x['m']) > 0 else 0 for x in par_heure]
        },
        'g2': {
            'labels': [x['media__channel_name'] for x in top_chaines],
            'taux': [round((x['f'] / (x['f'] + x['m'])) * 100, 1) if (x['f'] + x['m']) > 0 else 0 for x in top_chaines]
        },
        'g3': {
            'labels': ['Chaînes Publiques', 'Chaînes Privées'],
            'femmes': [x['f'] for x in public_priv],
            'hommes': [x['m'] for x in public_priv]
        },
        'g4': {
            'labels': ['00h-06h (Nuit)', '06h-00h (Journée)'],
            'taux_femmes': [taux_nuit, taux_jour]
        }
    })




def api_predictions_parole(request):
    data = predire_evolution_parole()
    return JsonResponse(data)








