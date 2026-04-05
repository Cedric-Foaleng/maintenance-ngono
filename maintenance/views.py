# pylint: disable=undefined-variable



# maintenance/views.py - IMPORTS COMPLÈTS
# IMPORTS CORRIGÉS (en HAUT de views.py)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import *  # ← IMPORT TOUT (SIMPLE & SANS ERREUR)


from io import BytesIO
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.template.loader import get_template
from datetime import datetime
import os
from xhtml2pdf import pisa

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

# IMPORTS CONDITIONNELS - UNIQUEMENT CE QUI EXISTE
try:
    from .models import (
        TypeFiche,
        Systeme,
        Composant,
        FicheSuivi,
        EvaluationComposant,
        AvisFiche,
        # PanneIntervention  ← COMMENTÉ pour l'instant
    )
    from .forms import HistoriquePanneForm, LigneHistoriqueFormSet
except ImportError:
    # Modèles manquants → on continue sans
    pass


# ------------------------
# Page d'accueil
# ------------------------
def page_accueil(request):
    return render(request, 'maintenance/accueil.html')

# ------------------------
# Authentification
# ------------------------
# INSCRIPTION
def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username} !')
            return redirect('connexion')
        else:
            messages.error(request, 'Erreur dans le formulaire')
    else:
        form = UserCreationForm()
    return render(request, 'maintenance/inscription.html', {'form': form})

# CONNEXION
def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bonjour {username}, bienvenue !')
                return redirect('tableau_de_bord')  # ou 'home'
        else:
            messages.error(request, 'Identifiants incorrects')
    else:
        form = AuthenticationForm()
    return render(request, 'maintenance/connexion.html', {'form': form})

def deconnexion_view(request):
    logout(request)
    return redirect('accueil')

# ------------------------
# Tableau de bord
# ------------------------
"""@login_required
def tableau_de_bord(request):
    types_fiche = TypeFiche.objects.all()
    nb_fiches = FicheSuivi.objects.count()
    #nb_pannes = PanneIntervention.objects.count()
    return render(request, 'maintenance/tableau_de_bord.html', {
        'types_fiche': types_fiche,
        'nb_fiches': nb_fiches,
        #'nb_pannes': nb_pannes,
    })"""
    
@login_required

def tableau_de_bord(request):
    nb_fiches = FicheSuivi.objects.filter(controleur=request.user).count()
    nb_pannes = HistoriquePanne.objects.filter(controleur=request.user).count()
    nb_systemes = Systeme.objects.count()  # ← AJOUTER CETTE LIGNE
    
    return render(request, 'maintenance/tableau_de_bord.html', {
        'nb_fiches': nb_fiches,
        'nb_pannes': nb_pannes,
        'nb_systemes': nb_systemes,
        'types_fiche': TypeFiche.objects.all()
    })


# ------------------------
# Gestion des types, systèmes, composants
# ------------------------
@login_required
def creer_type_fiche(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        if nom:
            TypeFiche.objects.create(nom=nom, description=description)
            return redirect('tableau_de_bord')
    return render(request, 'maintenance/creer_type_fiche.html')

@login_required
def creer_systeme(request, typefiche_id):
    type_fiche = get_object_or_404(TypeFiche, id=typefiche_id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        if nom:
            Systeme.objects.create(type_fiche=type_fiche, nom=nom)
            return redirect('tableau_de_bord')
    return render(request, 'maintenance/creer_systeme.html', {'type_fiche': type_fiche})

@login_required
def creer_composant(request, systeme_id):
    systeme = get_object_or_404(Systeme, id=systeme_id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        if nom:
            Composant.objects.create(systeme=systeme, nom=nom)
            return redirect('tableau_de_bord')
    return render(request, 'maintenance/creer_composant.html', {'systeme': systeme})

# ------------------------
# Fiches de suivi
# ------------------------
@login_required
def liste_fiches(request):
    fiches = FicheSuivi.objects.select_related('type_fiche', 'controleur').order_by('-date_creation')
    return render(request, 'maintenance/liste_fiches.html', {'fiches': fiches})

@login_required
def nouvelle_fiche(request, typefiche_id):
    type_fiche = get_object_or_404(TypeFiche, id=typefiche_id)
    systemes = type_fiche.systemes.prefetch_related('composants')

    if request.method == 'POST':
        with transaction.atomic():
            fiche = FicheSuivi.objects.create(
                type_fiche=type_fiche,
                controleur=request.user,
                commentaire_global=request.POST.get('commentaire_global', '')
            )
            for systeme in systemes:
                for composant in systeme.composants.all():
                    etat = request.POST.get(f"etat_{composant.id}")
                    decision = request.POST.get(f"decision_{composant.id}")
                    remarque = request.POST.get(f"remarque_{composant.id}", '')
                    if etat and decision:
                        EvaluationComposant.objects.create(
                            fiche=fiche,
                            composant=composant,
                            etat=etat,
                            decision=decision,
                            remarque=remarque
                        )
        return redirect('detail_fiche', fiche_id=fiche.id)

    return render(request, 'maintenance/nouvelle_fiche.html', {
        'type_fiche': type_fiche,
        'systemes': systemes,
    })

@login_required
def detail_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheSuivi, id=fiche_id)
    evaluations = fiche.evaluations.select_related('composant', 'composant__systeme')

    if request.method == 'POST':
        commentaire = request.POST.get('commentaire')
        if commentaire:
            AvisFiche.objects.create(
                fiche=fiche,
                auteur=request.user,
                commentaire=commentaire
            )

    avis = fiche.avis.select_related('auteur').order_by('-date_creation')
    return render(request, 'maintenance/detail_fiche.html', {
        'fiche': fiche,
        'evaluations': evaluations,
        'avis': avis,
    })

# ------------------------
# Export PDF
# ------------------------
"""@login_required
def export_pdf_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheSuivi, id=fiche_id)
    evaluations = fiche.evaluations.select_related('composant', 'composant__systeme')

    template_path = 'maintenance/fiche_pdf.html'
    context = {'fiche': fiche, 'evaluations': evaluations}
    template = get_template(template_path)
    html = template.render(context)

    # Réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_{fiche.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    # Sauvegarde sur disque
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'fiches_pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    with open(pdf_path, 'wb') as f:
        pisa.CreatePDF(html, dest=f)

    fiche.fichier_pdf.name = f'fiches_pdf/{filename}'
    fiche.save()

    return response
"""
@login_required
def export_pdf_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheSuivi, id=fiche_id)
    evaluations = fiche.evaluations.select_related('composant', 'composant__systeme')

    # NOUVEAU : Logo + Signature + Intervenant
    logo_url = f"{settings.STATIC_URL}maintenance/img/logo_entreprise.png"  # Ajuste chemin
    signature_url = getattr(fiche, 'intervenant_signature', None)
    if signature_url:
        signature_url = f"{settings.MEDIA_URL}{signature_url}"
    
    intervenant_nom = (
        getattr(fiche, 'intervenant_nom', None) or 
        request.user.get_full_name() or 
        request.user.username
    )

    template_path = 'maintenance/fiche_pdf.html'
    context = {
        'fiche': fiche, 
        'evaluations': evaluations,
        'logo_url': logo_url,
        'signature_url': signature_url,
        'intervenant_nom': intervenant_nom,
        'date_signature': getattr(fiche, 'date_signature', timezone.now())
    }
    
    template = get_template(template_path)
    html = template.render(context)

    # Réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_suivi_{fiche.id}_{intervenant_nom.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Génération PDF téléchargement
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    # Sauvegarde sur disque (ton code existant)
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'fiches_pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    with open(pdf_path, 'wb') as f:
        pisa.CreatePDF(html, dest=f)

    # Sauvegarde chemin fichier (ton code existant)
    fiche.fichier_pdf.name = f'fiches_pdf/{filename}'
    fiche.save()

    messages.success(request, f'✅ PDF généré avec signature : {filename}')
    return response


# ------------------------
# Espace commun
# ------------------------
"""@login_required
def espace_commun(request):
    fiches = FicheSuivi.objects.select_related('type_fiche', 'controleur').order_by('-date_creation')
    return render(request, 'maintenance/espace_commun.html', {'fiches': fiches})"""
    
@login_required
def espace_commun(request):
    """Espace commun FichesSuivi + HistoriquesPannes"""
    # Fiches de suivi existantes
    fiches = FicheSuivi.objects.select_related('type_fiche', 'controleur').order_by('-date_creation')
    
    # NOUVEAU : Historiques pannes
    try:
        from .models import HistoriquePanne
        historiques = HistoriquePanne.objects.select_related('controleur').order_by('-date')
        nb_historiques = historiques.count()
    except:
        historiques = []
        nb_historiques = 0
    
    return render(request, 'maintenance/espace_commun.html', {
        'fiches': fiches,
        'historiques': historiques,
        'nb_historiques': nb_historiques,
        'nb_fiches': fiches.count()
    })


@login_required
def creer_historique(request):
    if request.method == 'POST':
        form = HistoriquePanneForm(request.POST)
        formset = LigneHistoriqueFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            historique = form.save(commit=False)
            historique.controleur = request.user
            historique.save()
            formset.instance = historique
            formset.save()
            # Redirection vers la liste ou le PDF
            #return redirect('liste_historiques')
            return redirect('tableau_de_bord')  # ← FONCTIONNE

    else:
        form = HistoriquePanneForm()
        formset = LigneHistoriqueFormSet()
    return render(request, 'maintenance/creer_historique.html', {
        'form': form,
        'formset': formset,
    })

# ------------------------
# Pannes / interventions
# ------------------------


# ------------------------
# KPI (squelette simple)
# ------------------------
from django.db.models import Count

@login_required
def liste_historiques(request):
    """Liste toutes les fiches historiques"""
    try:
        from .models import HistoriquePanne
        historiques = HistoriquePanne.objects.select_related('controleur').order_by('-date')
    except:
        historiques = []
    return render(request, 'maintenance/liste_historiques.html', {'historiques': historiques})


@login_required
def kpi_view(request):
    stats_mauvais = (
        EvaluationComposant.objects
        .filter(etat='MAUVAIS')
        .values('fiche__type_fiche__nom')
        .annotate(total=Count('id'))
    )
    labels = [row['fiche__type_fiche__nom'] for row in stats_mauvais]
    data = [row['total'] for row in stats_mauvais]

    return render(request, 'maintenance/kpi.html', {
        'labels': labels,
        'data': data,
    })

#from django.shortcuts import render, redirect
#from django.contrib.auth.decorators import login_required



# ------------------------
# PDF Historique + Envoi Espace Commun
# ------------------------
def render_to_pdf(template_src, context_dict):
    """Génère PDF depuis template HTML"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

@login_required
def pdf_historique(request, pk):
    """Génère PDF fiche historique ET l'envoie à l'espace commun"""
    try:
        from .models import HistoriquePanne
        historique = get_object_or_404(HistoriquePanne, pk=pk)
    except:
        return HttpResponse("Modèle HistoriquePanne non disponible", status=500)
    
    context = {
        'historique': historique,
        'lignes': historique.lignes.all(),  # Suppose que tu as un related_name='lignes'
        'user': request.user,
        'date_pdf': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    # 1. GÉNÉRER PDF
    pdf_data = render_to_pdf('maintenance/pdf_historique.html', context)
    
    if not pdf_data:
        return HttpResponse("❌ Erreur génération PDF", status=500)
    
    # 2. TÉLÉCHARGER PDF
    response = HttpResponse(pdf_data, content_type='application/pdf')
    filename = f"historique_{historique.marque.replace(' ', '_')}_{historique.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # 3. ENVOYER à ESPACE COMMUN par email
    try:
        subject = f"🛠️ Fiche Historique - {historique.marque}"
        body = f"""Nouvelle fiche historique partagée par {request.user.username} :

MARQUE: {historique.marque}
DATE: {historique.date.strftime('%d/%m/%Y')}
HEURES: {historique.heure_fonctionnement}h

PDF en pièce jointe."""
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@maintenance.com',
            to=['espace.commun@maintenance.com'],  # Remplace par vrai email
            reply_to=[request.user.email]
        )
        email.attach(filename, pdf_data, 'application/pdf')
        email.send()
        
        messages.success(request, f"✅ PDF généré ET envoyé à l'espace commun ! ({filename})")
    except Exception as e:
        messages.warning(request, f"✅ PDF généré mais erreur envoi email: {str(e)}")
    
    return response



@login_required
def supprimer_historique(request, pk):
    """Supprimer un historique panne"""
    historique = get_object_or_404(HistoriquePanne, pk=pk)
    if request.method == 'POST':
        historique.delete()
        messages.success(request, f'✅ {historique.marque} supprimé !')
        return redirect('espace_commun')
    return render(request, 'maintenance/confirm_delete.html', {'objet': historique})

@login_required
def supprimer_fiche(request, pk):
    """Supprimer une fiche suivi"""
    fiche = get_object_or_404(FicheSuivi, pk=pk)
    if request.method == 'POST':
        fiche.delete()
        messages.success(request, f'✅ Fiche #{fiche.id} supprimée !')
        return redirect('espace_commun')
    return render(request, 'maintenance/confirm_delete.html', {'objet': fiche})

# VUES SYSTÈMES/COMPOSANTS (À AJOUTER)
from django.shortcuts import get_object_or_404
from .models import Systeme, Composant, FicheSuivi, LigneFicheSuivi

@login_required
def gerer_systemes_composants(request):
    """Gestion systèmes/composants POUR TOUS les contrôleurs"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'creer_systeme':
            Systeme.objects.create(
                nom=request.POST['nom_systeme'],
                icone=request.POST.get('icone_systeme', '⚙️'),
                cree_par=request.user
            )
            messages.success(request, '✅ Système créé !')
            
        elif action == 'creer_composant':
            Composant.objects.create(
                systeme_id=request.POST['systeme_id'],
                nom=request.POST['nom_composant'],
                unite_mesure=request.POST.get('unite_mesure', ''),
                tolerance_min=request.POST.get('tolerance_min'),
                tolerance_max=request.POST.get('tolerance_max'),
                cree_par=request.user
            )
            messages.success(request, '✅ Composant créé !')
            
        elif action == 'supprimer_systeme':
            systeme = get_object_or_404(Systeme, pk=request.POST['systeme_id'])
            systeme.delete()
            messages.success(request, '✅ Système supprimé !')
            
        elif action == 'supprimer_composant':
            composant = get_object_or_404(Composant, pk=request.POST['composant_id'])
            composant.delete()
            messages.success(request, '✅ Composant supprimé !')
    
    systemes = Systeme.objects.all()
    return render(request, 'maintenance/gerer_systemes.html', {'systemes': systemes})

@login_required
def creer_fiche_suivi_dynamique(request):
    """Fiche suivi dynamique systèmes/composants"""
    systemes = Systeme.objects.all()
    return render(request, 'maintenance/fiche_suivi_dynamique.html', {'systemes': systemes})
