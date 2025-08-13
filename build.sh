#!/usr/bin/env bash
# exit on error
set -o errexit

# Installe les dépendances
pip install -r requirements.txt

# Collecte les fichiers statiques
python manage.py collectstatic --noinput

# Applique les migrations de la base de données
python manage.py migrate
