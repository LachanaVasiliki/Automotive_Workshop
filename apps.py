# Διαμόρφωση της εφαρμογής "automotiveworkshop"

from django.apps import AppConfig


class AutomotiveWorkshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Ορισμός του τύπου του πεδίου auto field για την εφαρμογή
    name = 'automotiveworkshop'  # Ονομασία της εφαρμογής
