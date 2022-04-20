from django.urls import path

from .views import (  # QRCodeView,
    OptionsListView,
    QRVerify,
    RegisterCompleteView,
    RegisterView,
    RegistrationDataApi,
)

urlpatterns = [
    # path("qrcode/", QRCodeView.as_view(), name="qrcode"),
    path("register/<slug:slug>/", RegisterView.as_view(), name="register"),
    path("register/complete/<int:reg>/<int:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    path("options/<str:name>/<int:pk>/<int:label>/<str:parent>/", OptionsListView.as_view(), name="optionset"),
    path("api/data/<int:pk>/<int:start>/<int:end>/", RegistrationDataApi.as_view(), name="api"),
]
