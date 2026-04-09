from datetime import datetime, timedelta
from rest_framework import serializers
from doctors.models import Doctor
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor_name', 'customer_name',
            'date', 'start_time', 'end_time',
            'status', 'created_at'
        ]


class BookAppointmentSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField()

    def validate(self, data):
        try:
            doctor = Doctor.objects.get(pk=data['doctor_id'])
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("Doctor not found.")

        slot_start = datetime.combine(data['date'], data['start_time'])
        slot_end = slot_start + timedelta(minutes=doctor.slot_duration)

        data['end_time'] = slot_end.time()
        data['doctor'] = doctor
        return data