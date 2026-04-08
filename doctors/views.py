from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer, DoctorCreateSerializer, DoctorUpdateSerializer
from .permissions import IsSuperAdmin


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
            return Response(DoctorSerializer(doctor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)
        doctor.user.delete()  # deletes user and doctor profile via cascade
        return Response({'detail': 'Doctor deleted.'}, status=status.HTTP_200_OK)