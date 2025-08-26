from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import time, timedelta, datetime

"""
Ορισμός μοντέλων για εφαρμογή διαχείρισης συνεργείου αυτοκινήτων.
Τα μοντέλα περιλαμβάνουν:
1. Χρήστες (πελάτες, μηχανικοί, γραμματείς)
2. Αυτοκίνητα
3. Ραντεβού
4. Εργασίες
"""

class User(AbstractUser):
    """
    Προσαρμοσμένο μοντέλο χρήστη που επεκτείνει το AbstractUser του Django.
    Προσθέτει ρόλους και επιπλέον πληροφορίες για τους χρήστες.
    """
    ROLE_CHOICES = [
        ('client', 'Πελάτης'),
        ('mechanic', 'Μηχανικός'),
        ('secretary', 'Γραμματέας'),
    ]
    
    # Βασικά πεδία
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Ρόλος")
    afm = models.CharField(max_length=9, blank=True, null=True, verbose_name="ΑΤ")
    address = models.TextField(blank=True, null=True, verbose_name="Διεύθυνση")
    specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ειδικότητα")
    is_active = models.BooleanField(default=False, verbose_name="Ενεργός λογαριασμός")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Car(models.Model):
    """
    Μοντέλο για τα αυτοκίνητα των πελατών.
    Κάθε αυτοκίνητο ανήκει σε έναν πελάτη (client).
    """
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'client'},
        verbose_name="Ιδιοκτήτης"
    )
    serial_number = models.CharField(max_length=50, unique=True, verbose_name="Σειριακός αριθμός")
    model = models.CharField(max_length=100, verbose_name="Μοντέλο")
    make = models.CharField(max_length=100, verbose_name="Μάρκα")
    type = models.CharField(max_length=50, verbose_name="Τύπος")
    fuel_type = models.CharField(max_length=50, verbose_name="Καύσιμο")
    doors = models.PositiveIntegerField(verbose_name="Πόρτες")
    wheels = models.PositiveIntegerField(verbose_name="Τροχοί")
    production_date = models.DateField(verbose_name="Ημερομηνία παραγωγής")
    acquisition_year = models.PositiveIntegerField(verbose_name="Έτος απόκτησης")

    def __str__(self):
        return f"{self.make} {self.model} ({self.serial_number})"


class Appointment(models.Model):
    """
    Μοντέλο για τα ραντεβού στο συνεργείο.
    Κάθε ραντεβού σχετίζεται με πελάτη, αυτοκίνητο και μπορεί να έχει μηχανικό.
    """
    STATUS_CHOICES = [
        ('CREATED', 'Δημιουργήθηκε'),
        ('IN_PROGRESS', 'Σε εξέλιξη'),
        ('COMPLETED', 'Ολοκληρώθηκε'),
        ('CANCELLED', 'Ακυρώθηκε'),
    ]
    SERVICE_CHOICES = [
        ('service', 'Σέρβις'),
        ('repair', 'Επισκευή'),
    ]

    # Σχέσεις
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'client'},
        verbose_name="Πελάτης"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Αυτοκίνητο")
    mechanic = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='appointments',
        limit_choices_to={'role': 'mechanic'},
        verbose_name="Μηχανικός"
    )
    
    # Ημερομηνίες και ώρες
    date = models.DateField(verbose_name="Ημερομηνία")
    hour = models.TimeField(verbose_name="Ώρα")
    
    # Λοιπά πεδία
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, verbose_name="Τύπος υπηρεσίας")
    problem_description = models.TextField(blank=True, verbose_name="Περιγραφή προβλήματος")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Ημερομηνία δημιουργίας")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED', verbose_name="Κατάσταση")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Συνολικό κόστος")

    def clean(self):
        """Έλεγχος ότι τα ραντεβού είναι εντός ωραρίου λειτουργίας (8πμ-4μμ)"""
        if self.hour < time(8, 0) or self.hour > time(16, 0):
            raise ValidationError("Τα ραντεβού πρέπει να είναι μεταξύ 08:00 και 16:00.")

    def __str__(self):
        return f"Ραντεβού #{self.id} - {self.client.username}"

    @staticmethod
    def get_available_mechanic(appointment_date, appointment_hour):
        """
        Βρίσκει διαθέσιμο μηχανικό για συγκεκριμένη ημερομηνία και ώρα.
        Ελέγχει για υπερκαλυπτόμενα ραντεβού (διάρκεια 2 ώρες).
        """
        start_datetime = datetime.combine(appointment_date, appointment_hour)
        end_datetime = start_datetime + timedelta(hours=2)

        # Φίλτρα μόνο ενεργοί μηχανικοί
        all_mechanics = User.objects.filter(role='mechanic', is_active=True)
        available_mechanics = []

        for mech in all_mechanics:
            # Βρες όλα τα ραντεβού του μηχανικού που δεν έχουν ολοκληρωθεί
            overlapping = Appointment.objects.filter(
                mechanic=mech,
                date=appointment_date,
                hour__gte=time(8, 0),
                hour__lt=time(16, 0),
                status__in=['CREATED', 'IN_PROGRESS']
            )
            
            # Δημιουργία λίστας με τα υπάρχοντα ραντεβού του μηχανικού
            busy_times = [
                (datetime.combine(a.date, a.hour), datetime.combine(a.date, a.hour) + timedelta(hours=2))
                for a in overlapping
            ]
            
            # Έλεγχος για διαθεσιμότητα
            if all(not (start_datetime < b_end and end_datetime > b_start) for b_start, b_end in busy_times):
                available_mechanics.append(mech)

        # Επιστροφή τυχαίου διαθέσιμου μηχανικού (αν υπάρχει)
        if available_mechanics:
            import random
            return random.choice(available_mechanics)
        return None


class Work(models.Model):
    """
    Μοντέλο για τις εργασίες που πραγματοποιούνται σε κάθε ραντεβού.
    Κάθε εργασία σχετίζεται με ένα ραντεβού.
    """
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='works',
        verbose_name="Ραντεβού"
    )
    description = models.TextField(verbose_name="Περιγραφή")
    materials = models.TextField(verbose_name="Υλικά")
    completion_time = models.DurationField(verbose_name="Χρόνος ολοκλήρωσης")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Κόστος")

    def __str__(self):
        return f"Εργασία για Ραντεβού #{self.appointment.id}"