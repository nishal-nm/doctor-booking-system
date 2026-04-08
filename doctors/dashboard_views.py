from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from datetime import date

from accounts.models import User
from .models import Doctor, LeaveRequest
from .utils import generate_slots

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return redirect('dashboard_login')
        return view_func(request, *args, **kwargs)
    return wrapper


class DashboardLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.role == 'superadmin':
            return redirect('dashboard_home')
        return render(request, 'dashboard/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user and user.role == 'superadmin':
            login(request, user)
            return redirect('dashboard_home')
        messages.error(request, 'Invalid credentials or not a superadmin.')
        return render(request, 'dashboard/login.html')


class DashboardLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('dashboard_login')


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardHomeView(View):
    def get(self, request):
        total_doctors = Doctor.objects.count()
        pending_leaves = LeaveRequest.objects.filter(status='pending').count()
        return render(request, 'dashboard/home.html', {
            'total_doctors': total_doctors,
            'pending_leaves': pending_leaves,
        })


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardDoctorListView(View):
    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        return render(request, 'dashboard/doctors.html', {'doctors': doctors})


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardDoctorCreateView(View):
    def get(self, request):
        return render(request, 'dashboard/doctor_form.html', {
            'action': 'Create',
            'days': DAYS
        })

    def post(self, request):
        try:
            user = User.objects.create_user(
                email=request.POST['email'],
                full_name=request.POST['full_name'],
                password=request.POST['password'],
                role='doctor'
            )
            Doctor.objects.create(
                user=user,
                specialization=request.POST['specialization'],
                working_days=request.POST.getlist('working_days'),
                start_time=request.POST['start_time'],
                end_time=request.POST['end_time'],
                slot_duration=int(request.POST['slot_duration']),
                consultations_per_day=int(request.POST['consultations_per_day'])
            )
            messages.success(request, 'Doctor created successfully.')
            return redirect('dashboard_doctors')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'dashboard/doctor_form.html', {
                'action': 'Create',
                'days': DAYS
            })


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardDoctorUpdateView(View):
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        return render(request, 'dashboard/doctor_form.html', {
            'action': 'Update',
            'doctor': doctor,
            'days': DAYS
        })

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        try:
            doctor.specialization = request.POST['specialization']
            doctor.working_days = request.POST.getlist('working_days')
            doctor.start_time = request.POST['start_time']
            doctor.end_time = request.POST['end_time']
            doctor.slot_duration = int(request.POST['slot_duration'])
            doctor.consultations_per_day = int(request.POST['consultations_per_day'])
            doctor.save()
            messages.success(request, 'Doctor updated successfully.')
            return redirect('dashboard_doctors')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'dashboard/doctor_form.html', {
                'action': 'Update',
                'doctor': doctor,
                'days': DAYS
            })


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardDoctorDeleteView(View):
    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.user.delete()
        messages.success(request, 'Doctor deleted successfully.')
        return redirect('dashboard_doctors')


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardLeaveListView(View):
    def get(self, request):
        leaves = LeaveRequest.objects.select_related('doctor__user').all().order_by('-created_at')
        return render(request, 'dashboard/leaves.html', {'leaves': leaves})


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardLeaveUpdateView(View):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        new_status = request.POST.get('status')
        admin_remark = request.POST.get('admin_remark', '')
        if new_status in ['approved', 'rejected']:
            leave.status = new_status
            leave.admin_remark = admin_remark
            leave.save()
            messages.success(request, f'Leave request {new_status}.')
        return redirect('dashboard_leaves')


@method_decorator([login_required(login_url='dashboard_login'), superadmin_required], name='dispatch')
class DashboardSlotView(View):
    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        slots = []
        selected_doctor = None
        selected_date = None

        doctor_id = request.GET.get('doctor_id')
        date_str = request.GET.get('date')

        if doctor_id and date_str:
            try:
                selected_doctor = Doctor.objects.get(pk=doctor_id)
                selected_date = date.fromisoformat(date_str)
                slots = generate_slots(selected_doctor, selected_date)
            except (Doctor.DoesNotExist, ValueError):
                messages.error(request, 'Invalid doctor or date.')

        return render(request, 'dashboard/slots.html', {
            'doctors': doctors,
            'slots': slots,
            'selected_doctor': selected_doctor,
            'selected_date': selected_date,
        })