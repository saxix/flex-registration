from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template.base import render_value_in_context
from django.utils.safestring import SafeData, mark_safe

register = Library()


class TranslateNode(Node):
    child_nodelists = ()

    def __init__(self, filter_expression, noop, asvar=None, message_context=None):
        self.noop = noop
        self.asvar = asvar
        self.message_context = message_context
        self.filter_expression = filter_expression
        if isinstance(self.filter_expression.var, str):
            self.filter_expression.var = Variable("'%s'" % self.filter_expression.var)

    def render(self, context):
        self.filter_expression.var.translate = not self.noop
        if self.message_context:
            self.filter_expression.var.message_context = self.message_context.resolve(context)
        output = self.filter_expression.resolve(context)
        value = render_value_in_context(output, context)
        # Restore percent signs. Percent signs in template text are doubled
        # so they are not interpreted as string format flags.
        is_safe = isinstance(value, SafeData)
        value = value.replace("%%", "%")
        value = mark_safe(value) if is_safe else value
        if self.asvar:
            context[self.asvar] = value
            return ""
        else:
            return value


@register.tag("itranslate")
@register.tag("itrans")
def do_translate(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument" % bits[0])
    message_string = parser.compile_filter(bits[1])
    remaining = bits[2:]

    noop = False
    asvar = None
    message_context = None
    seen = set()
    invalid_context = {"as", "noop"}

    while remaining:
        option = remaining.pop(0)
        if option in seen:
            raise TemplateSyntaxError(
                "The '%s' option was specified more than once." % option,
            )
        elif option == "noop":
            noop = True
        elif option == "context":
            try:
                value = remaining.pop(0)
            except IndexError:
                raise TemplateSyntaxError("No argument provided to the '%s' tag for the context option." % bits[0])
            if value in invalid_context:
                raise TemplateSyntaxError(
                    "Invalid argument '%s' provided to the '%s' tag for the context " "option" % (value, bits[0]),
                )
            message_context = parser.compile_filter(value)
        elif option == "as":
            try:
                value = remaining.pop(0)
            except IndexError:
                raise TemplateSyntaxError("No argument provided to the '%s' tag for the as option." % bits[0])
            asvar = value
        else:
            raise TemplateSyntaxError(
                "Unknown argument for '%s' tag: '%s'. The only options "
                "available are 'noop', 'context' \"xxx\", and 'as VAR'."
                % (
                    bits[0],
                    option,
                )
            )
        seen.add(option)

    return TranslateNode(message_string, noop, asvar, message_context)
