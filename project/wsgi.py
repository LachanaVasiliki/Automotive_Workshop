import os

from django.core.wsgi import get_wsgi_application

# Ορισμός ρυθμίσεων για την WSGI εφαρμογή (Setting the settings for the WSGI application)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Επιστροφή της WSGI εφαρμογής (Returns the WSGI application)
application = get_wsgi_application()
