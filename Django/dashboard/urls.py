from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/parole/', views.data_temps_parole, name='api_parole'),
    path('api/themes/', views.data_themes_evolution, name='api_themes'),

    # Pages HTML pour la visualisation
    path('themes-jt/', views.page_themes_jt, name='page_themes_jt'),
    path('parole-global/', views.page_parole_global, name='page_parole_global'),
    path('parole-zoom/', views.page_parole_zoom, name='page_parole_zoom'),

    # API endpoints JSON
    path('api/themes-jt/', views.api_themes_jt, name='api_themes_jt'),
    path('api/parole-global/', views.api_parole_global, name='api_parole_global'),
    path('api/parole-zoom/', views.api_parole_zoom, name='api_parole_zoom'),

    path('api/predictions-parole/', views.api_predictions_parole, name='api_predictions_parole'),
]