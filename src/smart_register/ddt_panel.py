from debug_toolbar.panels import Panel
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from smart_register.state import state

TEMPLATE = """
<h2>{{state}}</h2>
<table>
<tr><th>request</th><td>{{state.request}}</td></tr>
{% for k,v in state.data.items %}
<tr><th>{{k}}</th><td>{{v}}</td></tr>
{% endfor %}
</table>

<h2>Info</h2>
<table>
<tr><th>User</th><td>{{state.user}}</td></tr>
<tr><th>  staff</th><td>{{state.user.is_staff}}</td></tr>
<tr><th>  superuser</th><td>{{state.user.is_superuser}}</td></tr>
</table>

"""


class StatePanel(Panel):
    name = "state"
    has_content = True

    def nav_title(self):
        return _("State")

    def title(self):
        return _("State Panel")

    def url(self):
        return ""

    @property
    def content(self):
        context = Context(
            {
                "state": state,
            }
        )
        template = Template(TEMPLATE)
        return template.render(context)
