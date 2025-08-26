from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    IndexView,
    CarCreateView,
    AppointmentCreateView,
    SecretaryAppointmentCreateView,
    AppointmentStatusUpdateView,
    RegisterView,
    MyAppointmentsView,
    MyCarsView,
    MyAssignedAppointmentsView,
    AllUsersView,
    AppointmentListView,
    CarListView,
    UserCSVUploadView,
    CarCSVUploadView,
    UserSearchView,
    CarSearchView,
    AppointmentSearchView

)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  #root URL
    path('cars/create/', CarCreateView.as_view(), name='car_create'),
    path('appointments/create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/create/by-secretary/', SecretaryAppointmentCreateView.as_view(), name='secretary_appointment_create'),
    path('appointments/<int:pk>/update-status/', AppointmentStatusUpdateView.as_view(), name='appointment_update_status'),
    path('appointments/mine/', MyAppointmentsView.as_view(), name='my_appointments'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('cars/mine/', MyCarsView.as_view(), name='my_cars'),
    path('appointments/assigned/', MyAssignedAppointmentsView.as_view(), name='my_assigned_appointments'),
    path('users/', AllUsersView.as_view(), name='all_users'),
    path('appointments/all/', AppointmentListView.as_view(), name='all_appointments'),
    path('cars/all/', CarListView.as_view(), name='all_cars'),
    path('upload/users/', UserCSVUploadView.as_view(), name='user_upload'),
    path('upload/cars/', CarCSVUploadView.as_view(), name='car_upload'),
    path('search/users/', UserSearchView.as_view(), name='user_search'),
    path('search/cars/', CarSearchView.as_view(), name='car_search'),
    path('search/appointments/', AppointmentSearchView.as_view(), name='appointment_search'),

]
