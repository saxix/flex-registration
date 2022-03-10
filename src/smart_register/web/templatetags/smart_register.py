from django.template import Library, Node
import six
from django.utils.functional import keep_lazy

register = Library()


class EscapeScriptNode(Node):
    def __init__(self, nodelist):
        super(EscapeScriptNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        out = self.nodelist.render(context)
        escaped_out = out.replace("</script>", "<\\/script>")
        return escaped_out


class LinebreaklessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        out = self.nodelist.render(context)
        escaped_out = out.replace("\n", "")
        return escaped_out


@register.tag()
def escapescript(parser, token):
    nodelist = parser.parse(("endescapescript",))
    parser.delete_first_token()
    return EscapeScriptNode(nodelist)


@register.tag()
def linebreakless(parser, token):
    nodelist = parser.parse(("endlinebreakless",))
    parser.delete_first_token()
    return LinebreaklessNode(nodelist)
