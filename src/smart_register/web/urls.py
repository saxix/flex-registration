from django.urls import path

from .views import OptionsListView, HomeView, RegisterCompleView, RegisterView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register-latest"),
    path("register/complete/", RegisterCompleView.as_view(), name="register-done"),
    path("options/<slug:name>/", OptionsListView.as_view(), name="optionset"),
]
