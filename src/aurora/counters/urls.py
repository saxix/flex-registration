from django.urls import path

from .views import MonthlyChartView, MonthlyDataView, index

app_name = "charts"

urlpatterns = [
    path("", index, name="index"),
    path("<int:registration>/monthly/", MonthlyChartView.as_view(), name="registration"),
    path("data/<int:registration_id>/monthly/", MonthlyDataView.as_view(), name="monthly_data"),
]
