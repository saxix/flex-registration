from django.urls import path

from .views import (
    HomeView,
    MaintenanceView,
    OptionsListView,
    PageView,
    ProbeView,
    QRCodeView,
    QRVerify,
    RegisterCompleteView,
    RegisterView,
    RegistrationDataApi,
)

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("page/<str:page>/", PageView.as_view(), name="page"),
    path("probe/", ProbeView.as_view(), name="probe"),
    path("qrcode/", QRCodeView.as_view(), name="qrcode"),
    path("maintenance", MaintenanceView.as_view(), name="maintenance"),
    path("register/<str:locale>/<slug:slug>/", RegisterView.as_view(), name="register"),
    # path("register/complete/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/complete/<int:pk>/<str:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    path("register/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    # path("reg/<str:locale>/<slug:slug>/", RegisterView.as_view(), name="register"),
    # path("reg/complete/", RegisterCompleteView.as_view(), name="register-done"),
    # path("reg/complete/<int:pk>/<str:rec>/", RegisterCompleteView.as_view(), name="register-done"),
    # path("reg/qr/<int:pk>/<str:hash>/", QRVerify.as_view(), name="register-verify"),
    # path("options/<str:name>/", OptionsListView.as_view(), name="optionset"),
    # re_path("options/(?P<name>)[a-z:_,-]/", OptionsListView.as_view(), name="optionset"),
    # path("options/<str:name>/<int:pk>/<int:label>/", OptionsListView.as_view(), name="optionset"),
    path("options/<str:name>/<int:pk>/<int:label>/<str:parent>/", OptionsListView.as_view(), name="optionset"),
    path("api/data/<int:pk>/<int:start>/<int:end>/", RegistrationDataApi.as_view(), name="api"),
]
