from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import get_language


@login_required()
def editor_info(request):
    data = {
        "authenticated": request.user.is_authenticated,
        "staff": request.user.is_staff,
        "canTranslate": request.user.is_staff,
        "languageCode": get_language(),
        "editUrl": reverse("admin:i18n_message_get_or_create"),
    }
    return JsonResponse(data)
