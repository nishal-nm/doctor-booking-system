from django.urls import path
from .views import (
    DoctorListCreateView, DoctorDetailView, 
    LeaveRequestView, LeaveStatusUpdateView,
    LeaveListAdminView, DoctorSlotView
)

urlpatterns = [
    path('', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:pk>/slots/', DoctorSlotView.as_view(), name='doctor-slots'),
    path('leaves/', LeaveRequestView.as_view(), name='leave-request'),
    path('leaves/all/', LeaveListAdminView.as_view(), name='leave-list-admin'),
    path('leaves/<int:pk>/status/', LeaveStatusUpdateView.as_view(), name='leave-status-update'),
]