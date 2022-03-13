from django.urls import path

from .views import OptionsListView
from .views import HomeView, RegisterCompleView, RegisterView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register-latest"),
    path("register/complete/", RegisterCompleView.as_view(), name="register-done"),
    path("options/<slug:name>/", OptionsListView.as_view(), name="optionset"),
    path("register/complete/<int:pk>/<int:rec>/", RegisterCompleView.as_view(), name="register-done"),
]
