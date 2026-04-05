from django.db import transaction
from .models import TypeFiche, Systeme, Composant

"""def load_initial_data():
    # Si au moins un type de fiche existe, on suppose que les données sont déjà chargées
    if TypeFiche.objects.exists():
        return"""
def load_initial_data(force=False):  # ← Ajoute force=False
    if TypeFiche.objects.exists() and not force:
        print("⚠️  Données existantes, passez force=True pour recharger")
        return
    
    # Reste du code...

    with transaction.atomic():
        # =========================
        # FICHE DE SUIVIE BANC VL
        # =========================
        banc_vl = TypeFiche.objects.create(
            nom="BANC VL",
            description="Fiche de suivi banc VL"
        )

        # PUPITRE - BANC VL
        pupitre_vl = Systeme.objects.create(type_fiche=banc_vl, nom="PUPITRE")
        composants_pupitre_vl = [
            "Ecran",
            "Tactile",
            "Nuc",
            "Clavier/télécommande",
            "Souris",
            "Onduleur",
            "Rallonge",
            "Cables/connexions",
            "Fixations",
            "Etat visuel",
        ]
        for nom in composants_pupitre_vl:
            Composant.objects.create(systeme=pupitre_vl, nom=nom)

        # ARMOIRE - BANC VL
        armoire_vl = Systeme.objects.create(type_fiche=banc_vl, nom="ARMOIRE")
        composants_armoire_vl = [
            "Carte",
            "Cables/connexions",
            "Disjoncteurs",
            "Contacteurs",
            "Soft starters",
            "Fixations",
            "Arrêt d’urgence",
            "Etat visuel",
        ]
        for nom in composants_armoire_vl:
            Composant.objects.create(systeme=armoire_vl, nom=nom)

        # RIPAGE - BANC VL
        ripage_vl = Systeme.objects.create(type_fiche=banc_vl, nom="RIPAGE")
        composants_ripage_vl = [
            "Fonctionnement",
            "Fixation",
            "Boulonnerie",
            "Roulements",
            "Etat visuel",
            "Cables/connexions",
        ]
        for nom in composants_ripage_vl:
            Composant.objects.create(systeme=ripage_vl, nom=nom)

        # SUSPENSION - BANC VL
        suspension_vl = Systeme.objects.create(type_fiche=banc_vl, nom="SUSPENSION")
        composants_suspension_vl = [
            "Fonctionnement",
            "Fixation",
            "Boulonnerie",
            "Capteur d’oscillation",
            "Cible capteur",
            "Moteur",
            "Paliers moteur",
            "Roulements",
            "Jauges de pesée",
            "Cables/connexions",
            "Etat visuel",
        ]
        for nom in composants_suspension_vl:
            Composant.objects.create(systeme=suspension_vl, nom=nom)

        # FREINAGE - BANC VL
        freinage_vl = Systeme.objects.create(type_fiche=banc_vl, nom="FREINAGE")
        composants_freinage_vl = [
            "Fonctionnement",
            "Rouleaux de freinage",
            "Chaines/pignons",
            "Jauges de frein",
            "Capteur de presence",
            "Capteur de vitesse",
            "Barre de présence",
            "Rouleaux de glissement",
            "Moteurs",
            "Reducteur",
            "Boulonnerie",
            "Cables/connexions",
            "Roulements",
            "Paliers moteur",
            "Paliers rouleaux",
            "Fouches du moteur",
            "Fixations",
            "Etat visuel",
        ]
        for nom in composants_freinage_vl:
            Composant.objects.create(systeme=freinage_vl, nom=nom)

        # POMPE VIDANGE FOSSE - BANC VL
        pompe_vl = Systeme.objects.create(type_fiche=banc_vl, nom="POMPE VIDANGE FOSSE")
        composants_pompe_vl = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_pompe_vl:
            Composant.objects.create(systeme=pompe_vl, nom=nom)

        # =========================
        # FICHE DE SUIVIE BANC PL
        # =========================
        banc_pl = TypeFiche.objects.create(
            nom="BANC PL",
            description="Fiche de suivi banc PL"
        )

        # PUPITRE - BANC PL
        pupitre_pl = Systeme.objects.create(type_fiche=banc_pl, nom="PUPITRE")
        composants_pupitre_pl = [
            "Ecran",
            "Tactile",
            "Nuc",
            "Clavier/télécommande",
            "Souris",
            "Onduleur",
            "Rallonge",
            "Cables/connexions",
            "Fixations",
            "Etat visuel",
        ]
        for nom in composants_pupitre_pl:
            Composant.objects.create(systeme=pupitre_pl, nom=nom)

        # ARMOIRE - BANC PL
        armoire_pl = Systeme.objects.create(type_fiche=banc_pl, nom="ARMOIRE")
        composants_armoire_pl = [
            "Carte",
            "Cables/connexions",
            "Disjoncteurs",
            "Contacteurs",
            "Soft starters",
            "Fixations",
            "Arrêt d’urgence",
            "Etat visuel",
        ]
        for nom in composants_armoire_pl:
            Composant.objects.create(systeme=armoire_pl, nom=nom)

        # RIPAGE - BANC PL
        ripage_pl = Systeme.objects.create(type_fiche=banc_pl, nom="RIPAGE")
        composants_ripage_pl = [
            "Fonctionnement",
            "Fixation",
            "Boulonnerie",
            "Roulements",
            "Etat visuel",
            "Cables/connexions",
        ]
        for nom in composants_ripage_pl:
            Composant.objects.create(systeme=ripage_pl, nom=nom)

        # FREINAGE - BANC PL
        freinage_pl = Systeme.objects.create(type_fiche=banc_pl, nom="FREINAGE")
        composants_freinage_pl = [
            "Fonctionnement",
            "Rouleaux de freinage",
            "Chaines/pignons",
            "Jauges de frein",
            "Capteur de presence",
            "Capteur de vitesse",
            "Barre de présence",
            "Rouleaux de glissement",
            "Moteurs",
            "Reducteur",
            "Boulonnerie",
            "Cables/connexions",
            "Roulements",
            "Paliers moteur",
            "Paliers rouleaux",
            "Fouches du moteur",
            "Amortisseurs",
        ]
        for nom in composants_freinage_pl:
            Composant.objects.create(systeme=freinage_pl, nom=nom)

        # MIROIR DE PISTE - BANC PL
        miroir_piste_pl = Systeme.objects.create(type_fiche=banc_pl, nom="MIROIR DE PISTE")
        composants_miroir_piste_pl = [
            "Fixations",
            "Etat visuel",
        ]
        for nom in composants_miroir_piste_pl:
            Composant.objects.create(systeme=miroir_piste_pl, nom=nom)

        # POMPE VIDANGE FOSSE - BANC PL
        pompe_pl = Systeme.objects.create(type_fiche=banc_pl, nom="POMPE VIDANGE FOSSE")
        composants_pompe_pl = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_pompe_pl:
            Composant.objects.create(systeme=pompe_pl, nom=nom)

        # =========================
        # FICHE DE SUIVIE AUXILIAIRES
        # =========================
        aux = TypeFiche.objects.create(
            nom="AUXILIAIRES",
            description="Fiche de suivi auxiliaires"
        )

        # COFFRET ELECTRIQUE
        coffret = Systeme.objects.create(type_fiche=aux, nom="COFFRET ELECTRIQUE")
        composants_coffret = [
            "Témoins",
            "Fusibles",
            "Disjoncteurs",
            "Contrôleur des phases",
            "Contacteurs",
            "Repartisseurs",
            "Parafoudre",
            "Cables/connexions",
            "Tension des phases",
            "Etat visuel",
        ]
        for nom in composants_coffret:
            Composant.objects.create(systeme=coffret, nom=nom)

        # PLAQUE A JEU VL
        plaque_jeu_vl = Systeme.objects.create(type_fiche=aux, nom="PLAQUE A JEU VL")
        composants_plaque_jeu_vl = [
            "Fonctionnement",
            "Fixations",
            "Boulonnerie",
            "Niveau d’huile",
            "Etanchéité",
            "Etat visuel",
        ]
        for nom in composants_plaque_jeu_vl:
            Composant.objects.create(systeme=plaque_jeu_vl, nom=nom)

        # CRIC PNEUMATIQUE DE FOSSE VL
        cric_vl = Systeme.objects.create(type_fiche=aux, nom="CRIC PNEUMATIQUE DE FOSSE VL")
        composants_cric_vl = [
            "Fonctionnement",
            "Fixations",
            "Boulonnerie",
            "Etanchéité",
            "Etat visuel",
        ]
        for nom in composants_cric_vl:
            Composant.objects.create(systeme=cric_vl, nom=nom)

        # PLAQUE A JEU PL
        plaque_jeu_pl = Systeme.objects.create(type_fiche=aux, nom="PLAQUE A JEU PL")
        composants_plaque_jeu_pl = [
            "Fonctionnement",
            "Fixations",
            "Boulonnerie",
            "Niveau d’huile",
            "Etanchéité",
            "Etat visuel",
        ]
        for nom in composants_plaque_jeu_pl:
            Composant.objects.create(systeme=plaque_jeu_pl, nom=nom)

        # REGLOPHARE VL
        reglo_vl = Systeme.objects.create(type_fiche=aux, nom="REGLOPHARE VL")
        composants_reglo_vl = [
            "Fonctionnement",
            "Batteries",
            "Laser",
            "chargeur",
            "Etat visuel",
        ]
        for nom in composants_reglo_vl:
            Composant.objects.create(systeme=reglo_vl, nom=nom)

        # REGLOPHARE PL
        reglo_pl = Systeme.objects.create(type_fiche=aux, nom="REGLOPHARE PL")
        composants_reglo_pl = [
            "Fonctionnement",
            "Batteries",
            "Laser",
            "chargeur",
            "Etat visuel",
        ]
        for nom in composants_reglo_pl:
            Composant.objects.create(systeme=reglo_pl, nom=nom)

        # ANALYSEUR DE GAZ
        analyseur = Systeme.objects.create(type_fiche=aux, nom="ANALYSEUR DE GAZ")
        composants_analyseur = [
            "Fonctionnement",
            "Chambre d’analyse",
            "Sonde de température",
            "Compte tour moteur",
            "Clavier/souris",
            "Ecran d’affichage",
            "Boite à fumée",
            "Câbles d’alimentations",
            "Etat visuel",
        ]
        for nom in composants_analyseur:
            Composant.objects.create(systeme=analyseur, nom=nom)

        # PEDOMETRE
        pedometre = Systeme.objects.create(type_fiche=aux, nom="PEDOMETRE")
        composants_pedometre = [
            "Fonctionnement",
            "Batterie",
            "Chargeur",
            "Etat visuel",
        ]
        for nom in composants_pedometre:
            Composant.objects.create(systeme=pedometre, nom=nom)

        # =========================
        # FICHE DE SUIVIE GENERATEUR
        # =========================
        gen = TypeFiche.objects.create(
            nom="GENERATEUR",
            description="Fiche de suivi groupe électrogène"
        )

        # GROUPE ELECTROGENE
        groupe = Systeme.objects.create(type_fiche=gen, nom="GROUPE ELECTROGENE")
        composants_groupe = [
            "Panneau de contrôle",
            "Tension débitée",
            "Régulateur de tension",
            "Alternateur",
            "Eléments d’insonorisation",
            "Supports de fixation",
            "Battants",
            "Boulonnerie",
            "Etat visuel",
        ]
        for nom in composants_groupe:
            Composant.objects.create(systeme=groupe, nom=nom)

        # INVERSEUR
        inverseur = Systeme.objects.create(type_fiche=gen, nom="INVERSEUR")
        composants_inverseur = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_inverseur:
            Composant.objects.create(systeme=inverseur, nom=nom)

        # BATTERIE
        batterie = Systeme.objects.create(type_fiche=gen, nom="BATTERIE")
        composants_batterie = [
            "Tension",
            "Cosses",
            "Etat visuel",
        ]
        for nom in composants_batterie:
            Composant.objects.create(systeme=batterie, nom=nom)

        # DEMARREUR
        demarreur = Systeme.objects.create(type_fiche=gen, nom="DEMARREUR")
        composants_demarreur = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_demarreur:
            Composant.objects.create(systeme=demarreur, nom=nom)

        # ALTERNATEUR DE CHARGE
        alternateur_charge = Systeme.objects.create(type_fiche=gen, nom="ALTERNATEUR DE CHARGE")
        composants_alternateur_charge = [
            "Fonctionnement",
            "tension de charge",
            "Poulie",
            "Courroie",
            "Etat visuel",
        ]
        for nom in composants_alternateur_charge:
            Composant.objects.create(systeme=alternateur_charge, nom=nom)

        # VENTILATEUR
        ventilateur = Systeme.objects.create(type_fiche=gen, nom="VENTILATEUR")
        composants_ventilateur = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_ventilateur:
            Composant.objects.create(systeme=ventilateur, nom=nom)

        # RADIATEUR
        radiateur = Systeme.objects.create(type_fiche=gen, nom="RADIATEUR")
        composants_radiateur = [
            "Bouchon de remplissage",
            "Bouchon de vidange",
            "Niveau",
            "Etat visuel",
        ]
        for nom in composants_radiateur:
            Composant.objects.create(systeme=radiateur, nom=nom)

        # POMPE A EAU
        pompe_eau = Systeme.objects.create(type_fiche=gen, nom="POMPE A EAU")
        composants_pompe_eau = [
            "Fonctionnement",
            "Etat visuel",
        ]
        for nom in composants_pompe_eau:
            Composant.objects.create(systeme=pompe_eau, nom=nom)

        # MOTEUR
        moteur = Systeme.objects.create(type_fiche=gen, nom="MOTEUR")
        composants_moteur = [
            "Fonctionnement",
            "Niveau d’huile",
            "Bouchon rempissa/vidange",
            "Injecteur",
            "Pompe d’injection",
            "Turbo",
            "La fumée",
            "Echappement",
            "Etat visuel",
        ]
        for nom in composants_moteur:
            Composant.objects.create(systeme=moteur, nom=nom)

        # RESERVOIR CARBURANT
        reservoir = Systeme.objects.create(type_fiche=gen, nom="RESERVOIR CARBURANT")
        composants_reservoir = [
            "Niveau",
            "Jauge",
            "Bouchon rempliss/vidange",
            "Etat visuel",
        ]
        for nom in composants_reservoir:
            Composant.objects.create(systeme=reservoir, nom=nom)

        # FILTRATION
        filtration = Systeme.objects.create(type_fiche=gen, nom="FILTRATION")
        composants_filtration = [
            "Filtre à air",
            "Ref filtre à air",
            "Filtre à huile",
            "Ref filtre à huile",
            "Préfiltre à gasoil",
            "Ref préfiltre à gasoil",
            "Filtre à gasoil",
            "Ref filtre à gasoil",
        ]
        for nom in composants_filtration:
            Composant.objects.create(systeme=filtration, nom=nom)
