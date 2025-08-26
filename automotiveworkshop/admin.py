# Εισαγωγή των απαραίτητων modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Car, Appointment, Work

"""
Ολόκληρος ο κώδικας ρυθμίζει τη διαχείριση των μοντέλων (User, Car, Appointment, Work)
στο Django Admin interface. Κάθε κλάση Admin ορίζει πώς θα εμφανίζονται και θα επεξεργάζονται
τα δεδομένα στο πίνακα διαχείρισης.
"""

# 1. ΡΥΘΜΙΣΗ ΤΟΥ ΜΟΝΤΕΛΟΥ ΧΡΗΣΤΗ (User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Προσαρμοσμένη διαχείριση χρηστών. Κληρονομεί από τη BaseUserAdmin του Django
    και προσθέτει επιπλέον πεδία (role, at, address).
    """
    
    # Επεκτείνουμε τα fieldsets της βασικής κλάσης με τα νέα μας πεδία
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Πρόσθετες Πληροφορίες", {
            "fields": ("role", "at", "address"),  # Τα προσαρμοσμένα πεδία του μοντέλου
            "description": "Επιπλέον πληροφορίες για τον χρήστη",  # Περιγραφή
        }),
    )
    
    # Τα πεδία που θα εμφανίζονται στη λίστα χρηστών
    list_display = ("username", "email", "role", "is_active", "is_staff")
    
    # Φίλτρα για εύκολη ταξινόμηση (δεξιά πλαϊνή μπάρα)
    list_filter = ("role", "is_active", "is_staff")
    
    # Που μπορεί να γίνει αναζήτηση (αναζητήσιμα πεδία)
    search_fields = ("username", "email", "at")


# 2. ΡΥΘΜΙΣΗ ΤΟΥ ΜΟΝΤΕΛΟΥ ΑΥΤΟΚΙΝΗΤΟΥ (Car)
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    """
    Διαχείριση μοντέλου αυτοκινήτων. Περιλαμβάνει βασικές πληροφορίες
    για κάθε αυτοκίνητο και σχέση με τον ιδιοκτήτη (owner).
    """
    
    list_display = ("serial_number", "make", "model", "owner")  # Οι στήλες που φαίνονται
    search_fields = ("serial_number", "make", "model")  # Που μπορώ να κάνω αναζήτηση
    list_filter = ("make", "fuel_type", "doors", "wheels")  # Φίλτρα ταξινόμησης
    
    # Χρήση αναζητήσιμου widget για το πεδίο owner (καλύτερο για πολλούς χρήστες)
    raw_id_fields = ("owner",)


# 3. ΡΥΘΜΙΣΗ ΤΩΝ ΡΑΝΤΕΒΟΥ (Appointment)
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Διαχείριση ραντεβού για service αυτοκινήτων. Περιλαμβάνει πληροφορίες
    για τον πελάτη, το αυτοκίνητο, την ημερομηνία και τον μηχανικό.
    """
    
    list_display = ("id", "client", "car", "date", "hour", "status", "mechanic")
    list_filter = ("status", "service_type", "date")  # Φίλτρα
    search_fields = ("client__username", "mechanic__username", "car__serial_number")  # Αναζήτηση σε σχετικά πεδία
    
    # Αναζητήσιμα widgets για τα σχετικά μοντέλα
    raw_id_fields = ("client", "car", "mechanic")


# 4. ΡΥΘΜΙΣΗ ΤΩΝ ΕΡΓΑΣΙΩΝ (Work)
@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """
    Διαχείριση εργασιών που πραγματοποιούνται σε κάθε ραντεβού.
    Περιλαμβάνει περιγραφή, χρόνο ολοκλήρωσης και κόστος.
    """
    
    list_display = ("appointment", "description", "completion_time", "cost")
    search_fields = ("description",)  # Μόνο στην περιγραφή μπορεί να γίνει αναζήτηση
    
    # Αναζητήσιμο widget για το σχετικό ραντεβού
    raw_id_fields = ("appointment",)