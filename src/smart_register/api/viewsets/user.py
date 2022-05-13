from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from smart_admin.smart_auth.admin import User

from .base import SmartViewSet


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("pk", "is_staff", "permissions")

    def get_permissions(self, obj):
        return obj.get_all_permissions()


class UserViewSet(SmartViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, permission_classes=[AllowAny], authentication_classes=[SessionAuthentication])
    def me(self, request):
        return Response({"perms": request.user.get_all_permissions(), "authenticated": request.user.is_authenticated})
