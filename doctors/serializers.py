from rest_framework import serializers
from accounts.models import User
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'email', 'specialization',
            'working_days', 'start_time', 'end_time',
            'slot_duration', 'consultations_per_day'
        ]


class DoctorCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)
    specialization = serializers.CharField()
    working_days = serializers.ListField(child=serializers.ChoiceField(choices=[
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    ]))
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    slot_duration = serializers.IntegerField(min_value=1)
    consultations_per_day = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            specialization=validated_data['specialization'],
            working_days=validated_data['working_days'],
            start_time=validated_data['start_time'],
            end_time=validated_data['end_time'],
            slot_duration=validated_data['slot_duration'],
            consultations_per_day=validated_data['consultations_per_day']
        )
        return doctor


class DoctorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'specialization', 'working_days', 'start_time',
            'end_time', 'slot_duration', 'consultations_per_day'
        ]

    def validate(self, data):
        start = data.get('start_time', self.instance.start_time)
        end = data.get('end_time', self.instance.end_time)
        if start >= end:
            raise serializers.ValidationError("Start time must be before end time.")
        return data