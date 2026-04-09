from datetime import date
from django.db import transaction, IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from doctors.permissions import IsCustomer, IsDoctor
from doctors.utils import generate_slots
from .models import Appointment
from .serializers import AppointmentSerializer, BookAppointmentSerializer


class DoctorListView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)


class AvailableSlotView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, pk):
        doctor = Doctor.objects.filter(pk=pk).select_related('user').first()
        if not doctor:
            return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': 'date query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        slots = generate_slots(doctor, slot_date)
        return Response({
            'doctor': DoctorSerializer(doctor).data,
            'date': date_str,
            'slots': slots
        })


class BookAppointmentView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if data['date'] < date.today():
            return Response({'detail': 'Cannot book an appointment for a past date.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor = data['doctor']
        appt_date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        available_slots = generate_slots(doctor, appt_date)
        requested = start_time.strftime('%H:%M')
        if not any(slot['start_time'] == requested for slot in available_slots):
            return Response({'detail': 'This slot is not available.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # lock existing rows for this doctor+date to prevent concurrent bookings
                list(Appointment.objects.select_for_update().filter(doctor=doctor, date=appt_date))

                overlapping = Appointment.objects.filter(
                    doctor=doctor,
                    date=appt_date
                ).filter(
                    Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
                )

                if overlapping.exists():
                    return Response(
                        {'detail': 'This slot overlaps with an existing appointment.'},
                        status=status.HTTP_409_CONFLICT
                    )

                appointment = Appointment.objects.create(
                    doctor=doctor,
                    customer=request.user,
                    date=appt_date,
                    start_time=start_time,
                    end_time=end_time
                )

        except IntegrityError:
            return Response(
                {'detail': 'This slot was just taken. Please choose another.'},
                status=status.HTTP_409_CONFLICT
            )

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class CustomerAppointmentListView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        appointments = Appointment.objects.filter(
            customer=request.user
        ).select_related('doctor__user')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class DoctorAppointmentListView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request):
        appointments = Appointment.objects.filter(
            doctor=request.user.doctor_profile
        ).select_related('customer')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)