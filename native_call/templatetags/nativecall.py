from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from native_call.exceptions import InvalidParameterTypeError
from native_call.registry import registry

register = template.Library()


@register.simple_tag
def dnc_script():
    return mark_safe(render_to_string('native_call/javascript.html', {}))


class NativeFunctionNode(template.Node):

    def __init__(self, function_name):
        self.function_name = function_name

    def render(self, context):
        from native_call.models import FunctionCallCSRF
        function = registry.get_function(self.function_name)
        if function:
            try:
                function.validate(context['user'])
                csrf = FunctionCallCSRF()
                csrf.function_name = self.function_name
                csrf.user = context['user']
                csrf.save()
                return 'dnc-csrf="{}"'.format(csrf.authorization_token)
            except InvalidParameterTypeError:
                pass
        return ''


@register.tag
def native_function(parser, token):
    try:
        tag_name, function_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    return NativeFunctionNode(function_name)
