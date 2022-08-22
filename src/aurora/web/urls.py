from django.contrib.auth.views import LoginView
from django.urls import path

from .views import HomeView, MaintenanceView, PageView, ProbeView, QRCodeView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("page/<str:page>/", PageView.as_view(), name="page"),
    path("probe/", ProbeView.as_view(), name="probe"),
    path("maintenance", MaintenanceView.as_view(), name="maintenance"),
    path("qrcode/", QRCodeView.as_view(), name="qrcode"),
    # # path("register/<str:locale>/<slug:slug>/", RegisterView.as_view(), name="register"),
    # path("register/<slug:slug>/", RegisterView.as_view(), name="register"),
    # path("register/complete/<int:reg>/<int:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    # path("register/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    # path("options/<str:name>/<int:pk>/<int:label>/<str:parent>/", OptionsListView.as_view(), name="optionset"),
    # path("api/data/<int:pk>/<int:start>/<int:end>/", RegistrationDataApi.as_view(), name="api"),
]
