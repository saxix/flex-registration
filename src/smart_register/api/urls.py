from django.urls import include, path
from rest_framework_nested import routers
from .views import RecordViewSet, SurveyViewSet, ApiRoot

router = routers.SimpleRouter()
router.register(r"surveys", SurveyViewSet)

domains_router = routers.NestedSimpleRouter(router, "surveys", lookup="surveys")
domains_router.register(r"records", RecordViewSet, basename="records")
# 'basename' is optional. Needed only if the same viewset is registered more than once
# Official DRF docs on this option: http://www.django-rest-framework.org/api-guide/routers/

app_name = "api"

urlpatterns = [
    path(r"", ApiRoot.as_view()),
    path(r"", include(router.urls)),
    path("auth/", include("rest_framework_social_oauth2.urls")),
]
