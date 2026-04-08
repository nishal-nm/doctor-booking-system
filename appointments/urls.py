from django.urls import path
from .views import (
    DoctorListView, AvailableSlotView,
    BookAppointmentView, CustomerAppointmentListView,
    DoctorAppointmentListView
)

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='customer-doctor-list'),
    path('doctors/<int:pk>/slots/', AvailableSlotView.as_view(), name='available-slots'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('my/', CustomerAppointmentListView.as_view(), name='customer-appointments'),
    path('doctor/my/', DoctorAppointmentListView.as_view(), name='doctor-appointments'),
]