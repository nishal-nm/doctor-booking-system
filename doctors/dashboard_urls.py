from django.urls import path
from .dashboard_views import (
    DashboardLoginView, DashboardLogoutView,
    DashboardHomeView, DashboardDoctorListView,
    DashboardDoctorCreateView, DashboardDoctorUpdateView,
    DashboardDoctorDeleteView, DashboardLeaveListView,
    DashboardLeaveUpdateView, DashboardSlotView
)

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='dashboard_home'),
    path('login/', DashboardLoginView.as_view(), name='dashboard_login'),
    path('logout/', DashboardLogoutView.as_view(), name='dashboard_logout'),
    path('doctors/', DashboardDoctorListView.as_view(), name='dashboard_doctors'),
    path('doctors/create/', DashboardDoctorCreateView.as_view(), name='dashboard_doctor_create'),
    path('doctors/<int:pk>/update/', DashboardDoctorUpdateView.as_view(), name='dashboard_doctor_update'),
    path('doctors/<int:pk>/delete/', DashboardDoctorDeleteView.as_view(), name='dashboard_doctor_delete'),
    path('leaves/', DashboardLeaveListView.as_view(), name='dashboard_leaves'),
    path('leaves/<int:pk>/update/', DashboardLeaveUpdateView.as_view(), name='dashboard_leave_update'),
    path('slots/', DashboardSlotView.as_view(), name='dashboard_slots'),
]