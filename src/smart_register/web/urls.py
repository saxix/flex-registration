from django.urls import path

from .views import DataSetListView, HomeView, RegisterCompleView, RegisterView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register"),
    path("register/", RegisterView.as_view(), name="register-last"),
    path("register/complete/", RegisterCompleView.as_view(), name="register-done"),
    path("data/", DataSetListView.as_view(), name="result"),
]
