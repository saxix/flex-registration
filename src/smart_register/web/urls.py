from django.urls import path

from .views import OptionsListView
from .views import HomeView, RegisterCompleView, RegisterView, MaintenanceView, ProbeView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("probe/", ProbeView.as_view(), name="probe"),
    path("maintenance", MaintenanceView.as_view(), name="maintenance"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register-latest"),
    path("register/complete/", RegisterCompleView.as_view(), name="register-done"),
    path("register/complete/<int:pk>/<int:rec>/", RegisterCompleView.as_view(), name="register-done"),
    path("options/<slug:name>/", OptionsListView.as_view(), name="optionset"),
]
