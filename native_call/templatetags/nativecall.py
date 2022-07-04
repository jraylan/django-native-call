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

        for arg in self.args:
            if arg.literal:
                parsedArgs.append(arg)
                continue
            try:
                parsedArgs.append(
                    arg.resolve(context)
                )
            except InvalidParameterTypeError as e:
                raise template.TemplateSyntaxError(str(e))

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
    args = bits[2:]
    parsed_args = []
    if args:
        for a in args:
            parsed_args.append(template.Variable(a))
    return NativeFunctionNode(function_name, parsed_args)
