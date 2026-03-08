from django import forms
from django.forms import inlineformset_factory
from .models import HistoriquePanne, LigneHistorique

class HistoriquePanneForm(forms.ModelForm):
    class Meta:
        model = HistoriquePanne
        fields = [
            'date', 'marque',
            'niveau_carburant', 'niveau_huile', 'niveau_eau',
            'heure_fonctionnement',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class LigneHistoriqueForm(forms.ModelForm):
    class Meta:
        model = LigneHistorique
        fields = [
            'equipement', 'symptomes', 'travaux',
            'methode_entretien', 'observations', 'outillage_pieces',
        ]

LigneHistoriqueFormSet = inlineformset_factory(
    HistoriquePanne,
    LigneHistorique,
    form=LigneHistoriqueForm,
    extra=1,
    can_delete=True,
)
