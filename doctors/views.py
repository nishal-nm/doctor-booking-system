from datetime import date as date_type
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Doctor, LeaveRequest
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, DoctorUpdateSerializer,
    LeaveRequestSerializer, LeaveStatusUpdateSerializer
)
from .permissions import IsSuperAdmin, IsDoctor
from .utils import generate_slots


class DoctorListCreateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get_object(self, pk):
        try:
            return Doctor.objects.select_related('user').get(pk=pk)
        except Doctor.DoesNotExist:
            return None

    def put(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DoctorUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            doctor.refresh_from_db()
            return Response(DoctorSerializer(doctor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)
        doctor.user.delete()  # cascades to doctor profile
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveRequestView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request):
        leaves = LeaveRequest.objects.filter(doctor=request.user.doctor_profile)
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveStatusUpdateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get_object(self, pk):
        try:
            return LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return None

    def put(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({'detail': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LeaveStatusUpdateSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            leave.refresh_from_db()
            return Response(LeaveRequestSerializer(leave).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveListAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        leaves = LeaveRequest.objects.select_related('doctor__user').all().order_by('-created_at')
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)


class DoctorSlotView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, pk):
        doctor = Doctor.objects.filter(pk=pk).select_related('user').first()
        if not doctor:
            return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': 'date query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot_date = date_type.fromisoformat(date_str)
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        slots = generate_slots(doctor, slot_date, for_admin=True)
        return Response({
            'doctor': DoctorSerializer(doctor).data,
            'date': date_str,
            'slots': slots
        })