# pylint: disable=undefined-variable
# maintenance/views.py - VERSION COMPLÈTE CORRIGÉE

import os
import base64
from datetime import datetime
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, HttpResponseForbidden
from django.db import transaction
from django.core.files.base import ContentFile  # ← CETTE LIGNE MANQUAIT
from django.core.files.storage import default_storage
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Count
from xhtml2pdf import pisa

# IMPORTS CONDITIONNELS - UNIQUEMENT CE QUI EXISTE
try:
    from .models import (
        TypeFiche,
        Systeme,
        Composant,
        FicheSuivi,
        EvaluationComposant,
        AvisFiche,
        HistoriquePanne,
    )
    from .forms import HistoriquePanneForm, LigneHistoriqueFormSet
except ImportError:
    pass


# ==================== PAGE D'ACCUEIL ====================

def page_accueil(request):
    return render(request, 'maintenance/accueil.html')


# ==================== AUTHENTIFICATION ====================

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
                return redirect('tableau_de_bord')
        else:
            messages.error(request, 'Identifiants incorrects')
    else:
        form = AuthenticationForm()
    return render(request, 'maintenance/connexion.html', {'form': form})


def deconnexion_view(request):
    logout(request)
    return redirect('accueil')


# ==================== TABLEAU DE BORD ====================

@login_required
def tableau_de_bord(request):
    nb_fiches = FicheSuivi.objects.filter(controleur=request.user).count()
    nb_pannes = HistoriquePanne.objects.filter(controleur=request.user).count()
    nb_systemes = Systeme.objects.count()
    
    return render(request, 'maintenance/tableau_de_bord.html', {
        'nb_fiches': nb_fiches,
        'nb_pannes': nb_pannes,
        'nb_systemes': nb_systemes,
        'types_fiche': TypeFiche.objects.all()
    })


# ==================== GESTION TYPES, SYSTÈMES, COMPOSANTS ====================

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


# ==================== FICHES DE SUIVI ====================

@login_required
def liste_fiches(request):
    fiches = FicheSuivi.objects.select_related('type_fiche', 'controleur').order_by('-date_creation')
    return render(request, 'maintenance/liste_fiches.html', {'fiches': fiches})


"""@login_required
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
"""

@login_required
def nouvelle_fiche(request, typefiche_id):
    type_fiche = get_object_or_404(TypeFiche, id=typefiche_id)
    systemes = type_fiche.systemes.prefetch_related('composants')

    if request.method == 'POST':
        with transaction.atomic():
            # 1. Création de la fiche (sans signature pour l'instant)
            fiche = FicheSuivi.objects.create(
                type_fiche=type_fiche,
                controleur=request.user,
                commentaire_global=request.POST.get('commentaire_global', '')
            )

            # 2. Collecte des évaluations SEULEMENT si la ligne est remplie
            evaluations_creees = 0

            for systeme in systemes:
                for composant in systeme.composants.all():
                    etat = request.POST.get(f"etat_{composant.id}", "").strip()
                    decision = request.POST.get(f"decision_{composant.id}", "").strip()
                    remarque = request.POST.get(f"remarque_{composant.id}", "").strip()

                    # On ne crée l'évaluation que si état ET décision sont remplis
                    if etat and decision:
                        EvaluationComposant.objects.create(
                            fiche=fiche,
                            composant=composant,
                            etat=etat,
                            decision=decision,
                            remarque=remarque
                        )
                        evaluations_creees += 1

            # 3. Validation minimale : au moins une ligne remplie
            if evaluations_creees == 0:
                # Annule tout et renvoie une erreur
                from django.contrib import messages
                messages.error(
                    request,
                    "Vous devez remplir au moins une ligne (état + décision) avant d'enregistrer."
                )
                # On supprime la fiche créée (transaction.atomic annule déjà les évaluations)
                fiche.delete()
                # On réaffiche le formulaire avec les données saisies
                return render(request, 'maintenance/nouvelle_fiche.html', {
                    'type_fiche': type_fiche,
                    'systemes': systemes,
                })

            # 4. Gestion de la signature numérique dessinée
            signataire_nom = request.POST.get('signataire_nom', '').strip()
            signature_dataurl = request.POST.get('signature', '').strip()

            # Si le client a signé et renseigné son nom
            if signature_dataurl and signataire_nom:
                if signature_dataurl.startswith('data:image/png;base64,'):
                    format_str, imgstr = signature_dataurl.split(';base64,', 1)
                    ext = format_str.split('/')[-1]

                    filename = f"sig_{request.user.id}_{fiche.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    image_data = base64.b64decode(imgstr)
                    content_file = ContentFile(image_data, name=filename)
                    saved_path = default_storage.save(f"signatures/{filename}", content_file)

                    fiche.signataire_nom = signataire_nom
                    fiche.signature = saved_path
                    fiche.date_signature = timezone.now()
                    fiche.save()

        # Si on arrive ici, au moins une évaluation a été créée → succès
        return redirect('detail_fiche', fiche_id=fiche.id)

    # Affichage du formulaire (GET)
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


# ==================== EXPORT PDF ====================

def link_callback(uri, rel):
    """Local static/media files for xhtml2pdf"""
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri[len(settings.STATIC_URL):])
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
    else:
        path = uri
    if os.path.exists(path):
        return path
    return None


"""@login_required
def export_pdf_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheSuivi, id=fiche_id)
    evaluations = fiche.evaluations.select_related('composant', 'composant__systeme')

    # Logo BASE64 (sûr)
    logo_base64 = None
    for path in [
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_ngono.png'),
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_entreprise.png')
    ]:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    logo_base64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
                break
            except Exception:
                continue

    context = {
        'fiche': fiche,
        'evaluations': evaluations,
        'logo_base64': logo_base64,
        'intervenant_nom': request.user.username,
    }

    html = render_to_string('maintenance/fiche_pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_{fiche.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('Erreur PDF', status=500)

    return response
"""

@login_required
def export_pdf_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheSuivi, id=fiche_id)
    evaluations = fiche.evaluations.select_related('composant', 'composant__systeme')

    # --- 1. Logo BASE64 (déjà existant) ---
    logo_base64 = None
    for path in [
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_ngono.png'),
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_entreprise.png')
    ]:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    logo_base64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
                break
            except Exception:
                continue

    # --- 2. SIGNATURE DESSINÉE EN BASE64 (NOUVEAU) ---
    signature_base64 = None
    if fiche.signature:
        try:
            # Construit le chemin absolu vers le fichier signature
            signature_path = default_storage.path(fiche.signature.name)
            if os.path.exists(signature_path):
                with open(signature_path, 'rb') as f:
                    signature_data = f.read()
                    signature_base64 = f"data:image/png;base64,{base64.b64encode(signature_data).decode('utf-8')}"
        except Exception:
            signature_base64 = None

    # --- 3. Contexte complet ---
    context = {
        'fiche': fiche,
        'evaluations': evaluations,
        'logo_base64': logo_base64,
        'signature_base64': signature_base64,  # ← C'EST ÇA QUI MANQUAIT
        'intervenant_nom': fiche.signataire_nom or request.user.username,
        'date_signature': fiche.date_signature or fiche.date_creation,
    }

    # --- 4. Génération du PDF ---
    html = render_to_string('maintenance/fiche_pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"fiche_{fiche.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('Erreur PDF', status=500)

    return response

# ==================== ESPACE COMMUN ====================

@login_required
def espace_commun(request):
    """Espace commun FichesSuivi + HistoriquesPannes"""
    fiches = FicheSuivi.objects.select_related('type_fiche', 'controleur').order_by('-date_creation')
    
    try:
        historiques = HistoriquePanne.objects.select_related('controleur').order_by('-date')
        nb_historiques = historiques.count()
    except Exception:
        historiques = []
        nb_historiques = 0
    
    return render(request, 'maintenance/espace_commun.html', {
        'fiches': fiches,
        'historiques': historiques,
        'nb_historiques': nb_historiques,
        'nb_fiches': fiches.count()
    })

"""
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
            return redirect('tableau_de_bord')
    else:
        form = HistoriquePanneForm()
        formset = LigneHistoriqueFormSet()
    return render(request, 'maintenance/creer_historique.html', {
        'form': form,
        'formset': formset,
    })
"""

@login_required
def creer_historique(request):
    if request.method == 'POST':
        form = HistoriquePanneForm(request.POST)
        formset = LigneHistoriqueFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            historique = form.save(commit=False)
            historique.controleur = request.user

            # ---- Gestion de la signature numérique ----
            signataire_nom = request.POST.get('signataire_nom', '').strip()
            signature_dataurl = request.POST.get('signature', '').strip()

            if signature_dataurl and signataire_nom:
                if signature_dataurl.startswith('data:image/png;base64,'):
                    format_str, imgstr = signature_dataurl.split(';base64,', 1)
                    ext = format_str.split('/')[-1]
                    filename = f"sig_panne_{request.user.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    image_data = base64.b64decode(imgstr)
                    content_file = ContentFile(image_data, name=filename)
                    saved_path = default_storage.save(f"signatures_panne/{filename}", content_file)

                    historique.signataire_nom = signataire_nom
                    historique.signature = saved_path
                    historique.date_signature = timezone.now()

            historique.save()

            formset.instance = historique
            formset.save()
            return redirect('tableau_de_bord')
    else:
        form = HistoriquePanneForm()
        formset = LigneHistoriqueFormSet()
    return render(request, 'maintenance/creer_historique.html', {
        'form': form,
        'formset': formset,
    })
# ==================== HISTORIQUES PANNES ====================

@login_required
def liste_historiques(request):
    """Liste toutes les fiches historiques"""
    try:
        historiques = HistoriquePanne.objects.select_related('controleur').order_by('-date')
    except Exception:
        historiques = []
    return render(request, 'maintenance/liste_historiques.html', {'historiques': historiques})


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
    try:
        historique = get_object_or_404(HistoriquePanne, pk=pk)
    except Exception:
        return HttpResponse("Modèle HistoriquePanne non disponible", status=500)
    
    lignes = historique.lignes.all()

    # --- 1. Logo BASE64 ---
    logo_base64 = None
    for path in [
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_ngono.png'),
        os.path.join(settings.STATIC_ROOT, 'maintenance/img/logo_entreprise.png')
    ]:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    logo_base64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
                break
            except Exception:
                continue

    # --- 2. Signature DESSINÉE en BASE64 ---
    signature_base64 = None
    if historique.signature:
        try:
            signature_path = default_storage.path(historique.signature.name)
            if os.path.exists(signature_path):
                with open(signature_path, 'rb') as f:
                    signature_data = f.read()
                    signature_base64 = f"data:image/png;base64,{base64.b64encode(signature_data).decode('utf-8')}"
        except Exception:
            signature_base64 = None

    context = {
        'historique': historique,
        'lignes': lignes,
        'user': request.user,
        'date_pdf': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'logo_base64': logo_base64,
        'signature_base64': signature_base64,
        'intervenant_nom': historique.signataire_nom or request.user.username,
        'date_signature': historique.date_signature or historique.date,
    }
    
    # 1. GÉNÉRER PDF
    pdf_data = render_to_pdf('maintenance/pdf_historique.html', context)
    
    if not pdf_data:
        return HttpResponse("❌ Erreur génération PDF", status=500)
    
    # 2. TÉLÉCHARGER PDF
    response = HttpResponse(pdf_data, content_type='application/pdf')
    filename = f"historique_{historique.marque.replace(' ', '_')}_{historique.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # 3. ENVOYER à ESPACE COMMUN par email (ton code existant)
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
            to=['espace.commun@maintenance.com'],
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


# ==================== GESTION SYSTÈMES/COMPOSANTS ====================

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


# ==================== KPI ====================

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