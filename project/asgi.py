import os

from django.core.asgi import get_asgi_application

# Ορισμός ρυθμίσεων για την ASGI εφαρμογή (Setting the settings for the ASGI application)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Επιστροφή της ASGI εφαρμογής (Returns the ASGI application)
application = get_asgi_application()
