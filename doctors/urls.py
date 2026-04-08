from django.urls import path
from .views import (
    DoctorListCreateView, DoctorDetailView, 
    LeaveRequestView, LeaveStatusUpdateView,
    DoctorSlotView
)

urlpatterns = [
    path('', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:pk>/slots/', DoctorSlotView.as_view(), name='doctor-slots'),
    path('leaves/', LeaveRequestView.as_view(), name='leave-request'),
    path('leaves/<int:pk>/status/', LeaveStatusUpdateView.as_view(), name='leave-status-update'),
]