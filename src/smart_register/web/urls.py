from django.urls import path

from .views import OptionsListView, QRCodeView
from .views import HomeView, RegisterCompleteView, RegisterView, MaintenanceView, ProbeView, QRVerify

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("probe/", ProbeView.as_view(), name="probe"),
    path("qrcode/", QRCodeView.as_view(), name="qrcode"),
    path("maintenance", MaintenanceView.as_view(), name="maintenance"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register-latest"),
    path("register/complete/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/complete/<int:pk>/<int:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    path("options/<slug:name>/", OptionsListView.as_view(), name="optionset"),
]
