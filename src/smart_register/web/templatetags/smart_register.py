from django.template import Library, Node

register = Library()


class EscapeScriptNode(Node):
    def __init__(self, nodelist):
        super(EscapeScriptNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        out = self.nodelist.render(context)
        escaped_out = out.replace("</script>", "<\\/script>")
        return escaped_out


@register.tag()
def escapescript(parser, token):
    nodelist = parser.parse(("endescapescript",))
    parser.delete_first_token()
    return EscapeScriptNode(nodelist)


@register.filter
def islist(value):
    return isinstance(value, (list, tuple))


@register.filter
def isdict(value):
    return isinstance(value, (dict,))


@register.inclusion_tag("dump/dump.html")
def dump(value):
    return {"value": value}


@register.inclusion_tag("dump/list.html")
def dump_list(value):
    return {"value": value}


@register.inclusion_tag("dump/dict.html")
def dump_dict(value):
    return {"value": value}
