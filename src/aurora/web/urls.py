from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    HomeView,
    MaintenanceView,
    PageView,
    ProbeView,
    QRCodeView,
    RegistrarLoginView,
    offline
)

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("login/", RegistrarLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("page/<str:page>/", PageView.as_view(), name="page"),
    path("probe/", ProbeView.as_view(), name="probe"),
    path("maintenance", MaintenanceView.as_view(), name="maintenance"),
    path("qrcode/", QRCodeView.as_view(), name="qrcode"),
    path("offline/", offline, name="offline"),
]
