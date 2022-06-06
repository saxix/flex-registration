from django.urls import path

from .views import (
    QRVerify,
    RegisterCompleteView,
    RegisterRouter,
    RegisterView,
    RegistrationDataApi,
)

urlpatterns = [
    path("route/", RegisterRouter.as_view(), name="registration-router"),
    path("register/complete/<int:reg>/<int:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    path("api/data/<int:pk>/<int:start>/<int:end>/", RegistrationDataApi.as_view(), name="api"),
    path("register/<slug:slug>/", RegisterView.as_view(), name="register"),
    path("register/<slug:slug>/<int:version>/", RegisterView.as_view(), name="register"),
    # path("register/<slug:slug>/<int:version>/<slug:key>/", RegisterView.as_view(), name="register"),
    # path("register/<slug:slug>/", RegisterView.as_view(), name="register"),
]
