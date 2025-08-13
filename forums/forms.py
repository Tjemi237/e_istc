from django import forms
from .models import SujetDiscussion, MessageForum

class SujetForm(forms.ModelForm):
    class Meta:
        model = SujetDiscussion
        fields = ['titre']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de votre sujet'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageForum
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Votre message...'}),
        }
        labels = {
            'contenu': '' # Pas de label pour le champ de réponse rapide
        }
