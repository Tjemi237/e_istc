from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

class EmailOrMatriculeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Essayer de trouver un utilisateur par matricule ou par username/email
            user = User.objects.get(Q(matricule=username) | Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
