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

    def __init__(self, function_name, args):
        self.function_name = function_name
        self.args = args

    def render(self, context):
        from native_call.models import FunctionCallCSRF
        function = registry.get_function(self.function_name)

        parsedArgs = []
        for a in self.args:
            if a in context:
                parsedArgs.append(context[a])
            else:
                parsedArgs.append(a)

        if function:
            try:
                function.validate(context['request'].user)
                csrf = FunctionCallCSRF()
                csrf.function_name = self.function_name
                csrf.user = context['request'].user
                csrf.args = str(parsedArgs)
                csrf.save()
                return 'dnc-csrf="{}"'.format(csrf.authorization_token)
            except InvalidParameterTypeError:
                pass
        return ''


@register.tag
def native_function(parser, token):
    bits = token.split_contents()
    try:
        tag_name, function_name = bits[:2]
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires at least one argument" % token.contents.split()[0])
    return NativeFunctionNode(function_name, bits[2:])
