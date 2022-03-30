from rest_framework import viewsets, generics

from .serializers import RegistrationSerializer, RecordSerializer
from smart_register.registration.models import Record, Registration


class ApiRoot(generics.GenericAPIView):
    name = "api-root"
    # def get(self, request, *args, **kwargs):
    #     return Response({
    #         'robot-categories': reverse(RobotCategoryList.name, request=request),
    #         'manufacturers': reverse(ManufacturerList.name, request=request),
    #         'robots': reverse(RobotList.name, request=request)
    #     })


class SurveyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
