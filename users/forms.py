from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from .models import User

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'matricule', 'specialite', 'photo')

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == User.Role.ETUDIANT and not user.username:
            user.username = user.matricule or user.email # Fallback if matricule is also empty
        user.set_unusable_password()
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'matricule', 'specialite', 'is_active', 'photo')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'matricule', 'specialite', 'photo', 'niveau_etude', 'filiere', 'statut_enseignant')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau_etude': forms.TextInput(attrs={'class': 'form-control'}),
            'filiere': forms.TextInput(attrs={'class': 'form-control'}),
            'statut_enseignant': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'profile-photo-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable/hide fields based on user role
        if self.instance.role == User.Role.ETUDIANT:
            self.fields['specialite'].required = False
            self.fields['specialite'].widget = forms.HiddenInput()
            self.fields['statut_enseignant'].required = False
            self.fields['statut_enseignant'].widget = forms.HiddenInput()
        elif self.instance.role == User.Role.ENSEIGNANT:
            self.fields['matricule'].required = False
            self.fields['matricule'].widget = forms.HiddenInput()
            self.fields['niveau_etude'].required = False
            self.fields['niveau_etude'].widget = forms.HiddenInput()
            self.fields['filiere'].required = False
            self.fields['filiere'].widget = forms.HiddenInput()
        else: # Admin or other roles, hide all specific fields
            self.fields['matricule'].required = False
            self.fields['matricule'].widget = forms.HiddenInput()
            self.fields['specialite'].required = False
            self.fields['specialite'].widget = forms.HiddenInput()
            self.fields['niveau_etude'].required = False
            self.fields['niveau_etude'].widget = forms.HiddenInput()
            self.fields['filiere'].required = False
            self.fields['filiere'].widget = forms.HiddenInput()
            self.fields['statut_enseignant'].required = False
            self.fields['statut_enseignant'].widget = forms.HiddenInput()
