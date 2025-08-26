from django import forms
from django.core.exceptions import ValidationError
from datetime import time
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, Car, Appointment, Work

# Χρησιμοποιούμε το ενεργό μοντέλο User του Django
User = get_user_model()

"""
Οι παρακάτω φόρμες χρησιμοποιούνται για:
1. Δημιουργία χρηστών
2. Καταχώρηση αυτοκινήτων
3. Διαχείριση ραντεβού
4. Καταγραφή εργασιών
"""

class CustomUserCreationForm(UserCreationForm):
    """
    Προσαρμοσμένη φόρμα δημιουργίας χρήστη που επεκτείνει την βασική UserCreationForm.
    """
    class Meta:
        model = User
        fields = ("username", "password1", "password2")  # Πεδία που θα εμφανίζονται

    def clean_username(self):
        """
        Ελέγχει αν το username είναι ήδη σε χρήση.
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Το όνομα χρήστη υπάρχει ήδη.")
        return username


class CarForm(forms.ModelForm):
    """
    Φόρμα για καταχώρηση και επεξεργασία αυτοκινήτων.
    Αποκλείει το πεδίο owner (θα ορίζεται αυτόματα).
    """
    class Meta:
        model = Car
        exclude = ['owner']  # Αποκλείουμε το πεδίο ιδιοκτήτη
    
    def clean_serial_number(self):
        """
        Ελέγχει αν ο σειριακός αριθμός υπάρχει ήδη στο σύστημα.
        """
        serial = self.cleaned_data['serial_number']
        if Car.objects.filter(serial_number=serial).exists():
            raise ValidationError("Υπάρχει ήδη αυτοκίνητο με αυτόν τον σειριακό αριθμό.")
        return serial


class AppointmentForm(forms.ModelForm):
    """
    Φόρμα για δημιουργία και επεξεργασία ραντεβού.
    Αποκλείει αυτόματα ορισμένα πεδία που θα ορίζονται από το σύστημα.
    """
    class Meta:
        model = Appointment
        exclude = ['mechanic', 'creation_date', 'status', 'total_cost']

    def clean_hour(self):
        """
        Ελέγχει αν η ώρα του ραντεβού είναι εντός ωραρίου (8:00-16:00).
        """
        hour = self.cleaned_data['hour']
        if hour < time(8, 0) or hour > time(16, 0):
            raise ValidationError("Τα ραντεβού πρέπει να είναι μεταξύ 08:00 και 16:00.")
        return hour

    def clean(self):
        """
        Επιπλέον έλεγχοι για την εγκυρότητα των δεδομένων:
        - Για επισκευές απαιτείται περιγραφή προβλήματος
        """
        cleaned_data = super().clean()
        if cleaned_data.get('service_type') == 'repair' and not cleaned_data.get('problem_description'):
            raise ValidationError("Απαιτείται περιγραφή προβλήματος για επισκευές.")
        return cleaned_data


class WorkForm(forms.ModelForm):
    """
    Φόρμα για καταχώρηση εργασιών που πραγματοποιήθηκαν σε ένα ραντεβού.
    """
    class Meta:
        model = Work
        fields = '__all__'  # Περιλαμβάνει όλα τα πεδία του μοντέλου

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")