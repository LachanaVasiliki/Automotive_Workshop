from django.views.generic import CreateView, UpdateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth import get_user_model
import random
import csv
from .forms import CSVUploadForm
from django.utils.decorators import method_decorator
from django.db.models import Q

from .models import Car, Appointment, User
from .forms import CarForm, AppointmentForm, CustomUserCreationForm
from .decorators import client_required, secretary_required, mechanic_required

"""
Οι παρακάτω views υλοποιούν τη λειτουργικότητα της εφαρμογής για:
- Πελάτες
- Μηχανικούς
- Γραμματείς
Χρησιμοποιούνται class-based views για καλύτερη οργάνωση και επαναχρησιμοποίηση κώδικα.
"""

class IndexView(View):
    """Απλή view για την αρχική σελίδα"""
    def get(self, request):
        return render(request, 'index.html')


class MyCarsView(LoginRequiredMixin, ListView):
    """
    Λίστα με τα αυτοκίνητα του τρέχοντα χρήστη (πελάτη).
    Χρησιμοποιεί το LoginRequiredMixin για έλεγχο σύνδεσης.
    """
    model = Car
    template_name = 'my_cars.html'
    context_object_name = 'cars'

    def get_queryset(self):
        """Φιλτράρει τα αυτοκίνητα βάσει ιδιοκτήτη"""
        return Car.objects.filter(owner=self.request.user)


@method_decorator(client_required, name='dispatch')
class CarCreateView(LoginRequiredMixin, CreateView):
    """
    View για δημιουργία νέου αυτοκινήτου από πελάτη.
    Χρησιμοποιεί decorator για έλεγχο ρόλου (client_required).
    """
    model = Car
    form_class = CarForm
    template_name = 'car_form.html'
    success_url = reverse_lazy('my_cars')  # Ανακατεύθυνση μετά την επιτυχία

    def form_valid(self, form):
        """Αυτόματη ανάθεση του τρέχοντα χρήστη ως ιδιοκτήτη"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


User = get_user_model()

@method_decorator(client_required, name='dispatch')
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('my_appointments')

    def form_valid(self, form):
        form.instance.client = self.request.user
        form.instance.status = 'CREATED'

        # τυχαιοσ μηχανικος
        mechanics = User.objects.filter(role='mechanic', is_active=True)
        if mechanics.exists():
            form.instance.mechanic = random.choice(mechanics)
        else:
            form.instance.mechanic = None  

        return super().form_valid(form)



@method_decorator(client_required, name='dispatch')
class MyAppointmentsView(LoginRequiredMixin, ListView):
    """
    Προβολή των ραντεβού του τρέχοντα πελάτη.
    Ταξινομείται με φθίνουσα σειρά ημερομηνίας/ώρας.
    """
    model = Appointment
    template_name = 'my_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(client=self.request.user).order_by('-date', '-hour')


class MyAssignedAppointmentsView(LoginRequiredMixin, ListView):
    """
    Προβολή των ανατεθειμένων ραντεβού για μηχανικό.
    """
    model = Appointment
    template_name = 'appointment_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(mechanic=self.request.user).order_by('date', 'hour')


@method_decorator(secretary_required, name='dispatch')
class SecretaryAppointmentCreateView(LoginRequiredMixin, CreateView):
    """
    View για δημιουργία ραντεβού από γραμματέα.
    Μπορεί να δημιουργήσει ραντεβού για οποιονδήποτε πελάτη.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'secretary_appointment_form.html'
    success_url = reverse_lazy('appointment_list')

    def form_valid(self, form):
        """Ορίζει μόνο την κατάσταση - τα υπόλοιπα τα ορίζει ο γραμματέας"""
        form.instance.status = 'CREATED'
        return super().form_valid(form)


@method_decorator(secretary_required, name='dispatch')
class AppointmentStatusUpdateView(LoginRequiredMixin, UpdateView):
    """
    Ενημέρωση κατάστασης ραντεβού από γραμματέα.
    Ελέγχει ότι δεν αλλάζει τελική κατάσταση (ολοκληρωμένο/ακυρωμένο).
    """
    model = Appointment
    fields = ['status']
    template_name = 'update_status.html'
    success_url = reverse_lazy('appointment_list')

    def form_valid(self, form):
        current_status = self.get_object().status
        new_status = form.cleaned_data['status']
        
        if current_status in ['COMPLETED', 'CANCELLED']:
            messages.error(self.request, "Δεν μπορείτε να αλλάξετε ένα τελικό στάδιο.")
            return redirect('appointment_detail', pk=self.get_object().pk)
            
        return super().form_valid(form)


@method_decorator(secretary_required, name='dispatch')
class AppointmentListView(LoginRequiredMixin, ListView):
    """
    Πλήρης λίστα ραντεβού για γραμματέα.
    """
    model = Appointment
    template_name = 'appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10  # Σελιδοποίηση ανά 10 εγγραφές

    def get_queryset(self):
        return Appointment.objects.all()


@method_decorator(client_required, name='dispatch')
class ClientAppointmentListView(LoginRequiredMixin, ListView):
    """
    Λίστα ραντεβού για πελάτη (μόνο τα δικά του).
    """
    model = Appointment
    template_name = 'client_appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        return Appointment.objects.filter(client=self.request.user)


@method_decorator(client_required, name='dispatch')
class ClientCarListView(LoginRequiredMixin, ListView):
    """
    Λίστα αυτοκινήτων για πελάτη (μόνο τα δικά του).
    """
    model = Car
    template_name = 'client_car_list.html'
    context_object_name = 'cars'
    paginate_by = 10

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)


@method_decorator(mechanic_required, name='dispatch')
class MechanicAppointmentListView(LoginRequiredMixin, ListView):
    """
    Λίστα ραντεβού για μηχανικό (μόνο τα ανατεθειμένα σε αυτόν).
    """
    model = Appointment
    template_name = 'mechanic_appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        return Appointment.objects.filter(mechanic=self.request.user)


class RegisterView(CreateView):
    """
    View για εγγραφή νέου χρήστη (πάντα ως πελάτης).
    """
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """Αυτόματη ρύθμιση ρόλου και ενεργοποίηση λογαριασμού"""
        user = form.save(commit=False)
        user.role = 'client'  # Οι νέοι χρήστες είναι πάντα πελάτες
        user.set_password(form.cleaned_data['password1'])
        user.is_active = True  # Αυτόματη ενεργοποίηση
        user.save()
        
        messages.success(self.request, "Η εγγραφή ήταν επιτυχής. Μπορείτε τώρα να συνδεθείτε.")
        return redirect(self.success_url)
    
class AllUsersView(ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'  # Make sure this template exists
    context_object_name = 'cars'

#εισαγωγη αρχειου csv
@method_decorator(secretary_required, name='dispatch')
class UserCSVUploadView(View):
    template_name = 'user_upload.html'

    def get(self, request):
        return render(request, self.template_name, {'form': CSVUploadForm()})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['csv_file']
            decoded = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)

            count = 0
            for row in reader:
                if not User.objects.filter(username=row['username']).exists():
                    User.objects.create_user(
                        username=row['username'],
                        password=row['password'],
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        email=row.get('email', ''),
                        role=row.get('role', 'client'),
                        afm=row.get('at', ''),
                        address=row.get('address', ''),
                        specialization=row.get('specialization', ''),
                        is_active=True
                    )
                    count += 1
            messages.success(request, f"{count} users imported.")
        return redirect('user_upload')
    

@method_decorator(secretary_required, name='dispatch')
class CarCSVUploadView(View):
    template_name = 'car_upload.html'

    def get(self, request):
        return render(request, self.template_name, {'form': CSVUploadForm()})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['csv_file']
            decoded = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)

            count = 0
            for row in reader:
                try:
                    owner = User.objects.get(username=row['owner_username'], role='client')
                    if not Car.objects.filter(serial_number=row['serial_number']).exists():
                        Car.objects.create(
                            owner=owner,
                            serial_number=row['serial_number'],
                            model=row['model'],
                            make=row['make'],
                            type=row['type'],
                            fuel_type=row['fuel_type'],
                            doors=int(row['doors']),
                            wheels=int(row['wheels']),
                            production_date=row['production_date'],
                            acquisition_year=int(row['acquisition_year'])
                        )
                        count += 1
                except Exception:
                    continue
            messages.success(request, f"{count} cars imported.")
        return redirect('car_upload')
    

#Βασικη αναζητηση για χρηστη
@method_decorator(secretary_required, name='dispatch')
class UserSearchView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'user_search.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return self.model.objects.filter(
            Q(username__icontains=query) |
            Q(last_name__icontains=query)
        )

#Βασικη αναζητηση για αμαξι
@method_decorator(secretary_required, name='dispatch')
class CarSearchView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'car_search.html'
    context_object_name = 'cars'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Car.objects.filter(
            Q(serial_number__icontains=query) |
            Q(make__icontains=query) |
            Q(model__icontains=query)
        )

#Βασικη αναζητηση για ραντεβου
@method_decorator(secretary_required, name='dispatch')
class AppointmentSearchView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointment_search.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Appointment.objects.filter(
            Q(client__last_name__icontains=query) |
            Q(client__afm__icontains=query) |
            Q(status__icontains=query)
        )
