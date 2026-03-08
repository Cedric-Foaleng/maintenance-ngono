from django.urls import path
from . import views

urlpatterns = [
   
    # La racine devient la page d’accueil publique
    path('', views.page_accueil, name='accueil'),

    # Tableau de bord sur une URL dédiée
    path('tableau_de_bord/', views.tableau_de_bord, name='tableau_de_bord'),
    

    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # Tableau de bord (après login)
    #path('', views.tableau_de_bord, name='tableau_de_bord'),

    # Fiches de suivi
    path('fiches/', views.liste_fiches, name='liste_fiches'),
    path('fiches/nouvelle/<int:typefiche_id>/', views.nouvelle_fiche, name='nouvelle_fiche'),
    path('fiches/<int:fiche_id>/', views.detail_fiche, name='detail_fiche'),
    path('fiches/<int:fiche_id>/pdf/', views.export_pdf_fiche, name='export_pdf_fiche'),

    # Espace commun
    path('espace-commun/', views.espace_commun, name='espace_commun'),

    # Pannes / interventions
    #path('pannes/', views.liste_pannes, name='liste_pannes'),
    #path('pannes/nouvelle/', views.nouvelle_panne, name='nouvelle_panne'),


    path('historiques/nouveau/', views.creer_historique, name='creer_historique'),
    # plus tard : liste, détail, PDF...



    # KPI
    path('kpi/', views.kpi_view, name='kpi'),
    
    
    # ... tes urls existantes
    path('historiques/<int:pk>/pdf/', views.pdf_historique, name='pdf_historique'),
    
   
    # ... tes autres urls
    path('historiques/', views.liste_historiques, name='liste_historiques'),
    path('historiques/<int:pk>/pdf/', views.pdf_historique, name='pdf_historique'),
    path('historiques/nouveau/', views.creer_historique, name='creer_historique'),


    path('supprimer-historique/<int:pk>/', views.supprimer_historique, name='supprimer_historique'),
    path('supprimer-fiche/<int:pk>/', views.supprimer_fiche, name='supprimer_fiche'),

    path('gerer-systemes/', views.gerer_systemes_composants, name='gerer_systemes'),
    path('fiche-suivi-dynamique/', views.creer_fiche_suivi_dynamique, name='creer_fiche_suivi_dynamique'),



]
"""
from django.urls import path
from . import views

urlpatterns = [
    # Page d’accueil
    path('', views.page_accueil, name='accueil'),

    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # Tableau de bord
    path('tableau_de_bord/', views.tableau_de_bord, name='tableau_de_bord'),

    # Fiches de suivi
    path('fiches/', views.liste_fiches, name='liste_fiches'),
    path('fiches/nouvelle/<int:typefiche_id>/', views.nouvelle_fiche, name='nouvelle_fiche'),
    path('fiches/<int:fiche_id>/', views.detail_fiche, name='detail_fiche'),
    path('fiches/<int:fiche_id>/pdf/', views.export_pdf_fiche, name='export_pdf_fiche'),

    # Espace commun
    path('espace-commun/', views.espace_commun, name='espace_commun'),

    # Pannes / interventions (si tu veux les réactiver)
    path('pannes/', views.liste_pannes, name='liste_pannes'),
    path('pannes/nouvelle/', views.nouvelle_panne, name='nouvelle_panne'),

    # Historique pannes/interventions – FORMULAIRE UTILISATEUR
    path('historiques/nouveau/', views.creer_historique, name='creer_historique'),

    # KPI
    path('kpi/', views.kpi_view, name='kpi'),
]
"""