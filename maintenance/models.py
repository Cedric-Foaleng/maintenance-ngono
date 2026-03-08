from django.db import models
from django.contrib.auth.models import User

# ========================================
# 1. CHOICES (en HAUT - global)
# ========================================
ETAT_CHOICES = [
    ('BON', 'BON'),
    ('PASSABLE', 'PASSABLE'),
    ('MAUVAIS', 'MAUVAIS'),
]

DECISION_CHOICES = [
    ('REPARER', 'Réparer'),
    ('NE_PAS_REPARER', 'Ne pas réparer'),
]

METHODE_CHOICES = [
    ('depannage', "Dépannage"),
    ('reparation', "Réparation"),
    ('entretien_conduite', "Entretien de conduite"),
    ('entretien_preventif', "Entretien préventif conditionnel"),
    ('entretien_systematique', "Entretien systématique"),
    ('amelioration', "Amélioration"),
]

# ========================================
# 2. MODÈLES - ORDRE STRICT (pas de doublons/circularité)
# ========================================

# 1️⃣ TypeFiche (BASE)
class TypeFiche(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Types de fiches"
    
    def __str__(self):
        return self.nom

# 2️⃣ Systeme (dépend TypeFiche)
class Systeme(models.Model):
    type_fiche = models.ForeignKey(TypeFiche, on_delete=models.CASCADE, related_name='systemes')
    nom = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Systèmes"
    
    def __str__(self):
        return f"{self.type_fiche.nom} - {self.nom}"

# 3️⃣ Composant (dépend Systeme)
class Composant(models.Model):
    systeme = models.ForeignKey(Systeme, on_delete=models.CASCADE, related_name='composants')
    nom = models.CharField(max_length=100)
    unite_mesure = models.CharField(max_length=20, blank=True, default='')
    tolerance_min = models.FloatField(null=True, blank=True)
    tolerance_max = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Composants"
        unique_together = ['systeme', 'nom']
    
    def __str__(self):
        return f"{self.systeme.nom} - {self.nom}"

# 4️⃣ FicheSuivi (dépend TypeFiche)
class FicheSuivi(models.Model):
    type_fiche = models.ForeignKey(TypeFiche, on_delete=models.CASCADE, related_name='fiches')
    controleur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    commentaire_global = models.TextField(blank=True)
    fichier_pdf = models.FileField(upload_to='fiches_pdf/', null=True, blank=True)
    
    def __str__(self):
        return f"Fiche {self.type_fiche.nom} #{self.id}"

# 5️⃣ EvaluationComposant (dépend FicheSuivi + Composant)
class EvaluationComposant(models.Model):
    fiche = models.ForeignKey(FicheSuivi, on_delete=models.CASCADE, related_name='evaluations')
    composant = models.ForeignKey(Composant, on_delete=models.CASCADE)
    etat = models.CharField(max_length=10, choices=ETAT_CHOICES)
    decision = models.CharField(max_length=15, choices=DECISION_CHOICES)
    remarque = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Évaluations composants"
        unique_together = ('fiche', 'composant')
    
    def __str__(self):
        return f"{self.composant} - {self.etat}"

# 6️⃣ AvisFiche (dépend FicheSuivi)
class AvisFiche(models.Model):
    fiche = models.ForeignKey(FicheSuivi, on_delete=models.CASCADE, related_name='avis')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Avis de {self.auteur.username} sur fiche {self.fiche.id}"

# 7️⃣ HistoriquePanne (indépendant)
class HistoriquePanne(models.Model):
    date = models.DateField()
    marque = models.CharField(max_length=100)
    niveau_carburant = models.CharField(max_length=50, blank=True)
    niveau_huile = models.CharField(max_length=50, blank=True)
    niveau_eau = models.CharField(max_length=50, blank=True)
    heure_fonctionnement = models.CharField(max_length=50, blank=True)
    controleur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.marque} - {self.date}"

# 8️⃣ LigneHistorique (dépend HistoriquePanne)
class LigneHistorique(models.Model):
    historique = models.ForeignKey(HistoriquePanne, on_delete=models.CASCADE, related_name='lignes')
    equipement = models.CharField(max_length=150)
    symptomes = models.TextField()
    travaux = models.TextField()
    methode_entretien = models.CharField(max_length=30, choices=METHODE_CHOICES)
    observations = models.TextField(blank=True)
    outillage_pieces = models.TextField(blank=True, verbose_name="Outillages / pièces")
    
    def __str__(self):
        return f"{self.equipement} - {self.symptomes[:30]}"

# 9️⃣ LigneFicheSuivi (NOUVEAU - dépend FicheSuivi + Composant)
class LigneFicheSuivi(models.Model):
    fiche = models.ForeignKey(FicheSuivi, on_delete=models.CASCADE, related_name='lignes_suivi')
    composant = models.ForeignKey(Composant, on_delete=models.CASCADE)
    valeur_mesuree = models.FloatField()
    observation = models.TextField(blank=True)
    conforme = models.BooleanField(default=True)
    date_mesure = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Lignes fiches suivi"
    
    def __str__(self):
        return f"{self.composant} - {self.valeur_mesuree}"
