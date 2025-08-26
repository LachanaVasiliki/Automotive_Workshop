from django.contrib import admin
from django.urls import include, path

# Ρυθμίσεις δρομολόγησης URL (URL routing settings)
urlpatterns = [
    path('admin/', admin.site.urls),  # Διαχειριστικό πάνελ (Admin Panel)
    path('', include("automotiveworkshop.urls"))  # Εφαρμογή συστήματος (Include URLs from the automotiveworkshop app)
]
