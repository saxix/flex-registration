from django.contrib.auth.views import LoginView


class RegistrarLoginView(LoginView):
    template_name = "registration/login.html"
