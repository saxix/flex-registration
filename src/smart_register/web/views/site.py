import base64
import io
from pathlib import Path

import qrcode
from PIL import Image
from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [config.HOME_TEMPLATE, self.template_name]


class QRCodeView(TemplateView):
    template_name = "qrcode.html"

    def get_qrcode(self, content):
        logo_link = Path(settings.BASE_DIR) / "web/static/unicef_logo.jpeg"
        logo = Image.open(logo_link)
        basewidth = 100
        wpercent = basewidth / float(logo.size[0])
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        QRcode.add_data(content)
        QRcode.make()
        QRimg = QRcode.make_image(fill_color="black", back_color="white").convert("RGB")

        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
        buff = io.BytesIO()
        # save the QR code generated
        QRimg.save(buff, format="PNG")
        return base64.b64encode(buff.getvalue()).decode()

    def get_context_data(self, **kwargs):
        url = self.request.build_absolute_uri("/")
        qrcode = self.get_qrcode(url)
        return super().get_context_data(**kwargs, qrcode=qrcode, url=url)


class ProbeView(View):
    http_method_names = ["get", "head"]

    def head(self, request, *args, **kwargs):
        return HttpResponse("Ok")

    def get(self, request, *args, **kwargs):
        return HttpResponse("Ok")


def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)


class MaintenanceView(TemplateView):
    template_name = "maintenance.html"

    def get(self, request, *args, **kwargs):
        if not config.MAINTENANCE_MODE:
            return HttpResponseRedirect("/")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
