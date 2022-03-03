from django.urls import path

from .views import RegisterCompleView, DataSetListView, RegisterView, HomeView

urlpatterns = [
    path('', HomeView.as_view()),
    path('register/', RegisterView.as_view(), name="register-last"),
    path('register/<int:pk>/', RegisterView.as_view(), name="register"),
    path('register/complete/', RegisterCompleView.as_view(), name="register-done"),
    path('data/', DataSetListView.as_view(), name="result"),
]
