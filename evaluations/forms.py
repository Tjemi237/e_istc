from django import forms
from .models import Activite, Question, Choix, QuestionSondage, ReponseSondage, Soumission

class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = ['title', 'description', 'activity_type', 'due_date']

class QuestionSondageForm(forms.ModelForm):
    class Meta:
        model = QuestionSondage
        fields = ['intitule']

class ReponseSondageForm(forms.ModelForm):
    class Meta:
        model = ReponseSondage
        fields = ['reponse']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['intitule', 'type_question']

class ChoixForm(forms.ModelForm):
    class Meta:
        model = Choix
        fields = ['texte', 'est_correct']

class SoumissionForm(forms.ModelForm):
    class Meta:
        model = Soumission
        fields = ['fichier']
