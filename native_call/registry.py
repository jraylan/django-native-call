import traceback

from django.db import transaction

from .constants import *
from .exceptions import *
from .wrapper import WrappedFunction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import inspect
import json
import re
import types

try:
    from django.urls import url
except ImportError:
    from django.urls import path as url


class Registry:
    __registered_functions = {}

    def register(
            self,
            name=None,
            arg_types=[],
            permissions=[],
            allow_anonymous=False
    ):
        if name:
            try:
                assert re.match(JS_RESERVED_REGEX, name)
            except AssertionError:
                raise InvalidRegistrationException(
                    'The identifier "{}" given in parameter "name" is a javascript reserved word'.format(name)
                )

            try:
                assert re.match(JS_VALIDATOR_REGEX, name)
            except AssertionError:
                raise InvalidRegistrationException("The parameter name must be a javascript friendly function name")

        if arg_types:
            try:
                assert isinstance(arg_types, (list, tuple))
            except AssertionError:
                InvalidRegistrationException('The parameter "arg_types" must be a list or tuple')

            for invalid_el in filter(lambda el: el not in ALLOWED_ARG_TYPE, arg_types):
                raise InvalidRegistrationException(
                    'Item of type "{}" in arg_types is invalid. Allowed values are {}'.format(
                        invalid_el if isinstance(invalid_el, type) else type(invalid_el),
                        ', '.join([c.__name__ for c in ALLOWED_ARG_TYPE])
                    )
                )

        try:
            assert isinstance(permissions, (list, tuple))
        except AssertionError:
            InvalidRegistrationException('The parameter "permissions" must be a list or tuple')

        try:
            assert isinstance(allow_anonymous, bool)
        except AssertionError:
            InvalidRegistrationException('The parameter "allow_anonymous" must be ether True or False')

        def decorator(func):
            try:
                assert isinstance(func, types.FunctionType)
            except AssertionError:
                InvalidRegistrationException('Registered entity must be a function')

            _name = name

            if not _name:
                _name = func.__name__

            kwargs = inspect.getfullargspec(func).varkw

            try:
                assert not kwargs
            except AssertionError:
                raise InvalidParameterTypeError(
                    'Keyword aggregation arguments "{}" are not supported'.format(kwargs)
                )

            _wrapped_function_ = WrappedFunction(func, _name, arg_types, permissions, allow_anonymous)

            if _name in self.__registered_functions:
                raise FunctionAlreadyRegisteredException(
                    'There\'s already a function registered with this name: "{}"'.format(_name)
                )

            self.__registered_functions[_name] = {
                "wrapper": _wrapped_function_,
            }

            return _wrapped_function_

        return decorator

    def get_function(self, name):
        return self.__registered_functions.get(name, {}).get('wrapper')

    def view(self, request):
        if request.method != 'POST':
            return HttpResponse("{}", status=405)

        from . import models
        with transaction.atomic():
            call_csrf = get_object_or_404(
                models.FunctionCallCSRF,
                authorization_token=request.POST.get('dnc_csrf'),
                user_id=request.user.id
            )
            call_csrf = models.FunctionCallCSRF.objects.select_for_update().get(id=call_csrf.id)

            new_call_csrf = models.FunctionCallCSRF()
            new_call_csrf.user.id = request.user.id
            new_call_csrf.function_name = call_csrf.function_name
            new_call_csrf.save()
            call_csrf.delete()

        function_name = str(call_csrf.function_name)
        
        params = request.POST.getlist('params[]') or []

        function = self.get_function(function_name)

        if not function.validate(request.user, params):
            response = HttpResponse('{}', status=401)
        else:
            # noinspection PyBroadException
            try:
                result = function(*params)

                try:
                    result = json.dumps(result)
                except TypeError:
                    response = HttpResponse('{}', status=500)
                else:
                    response = HttpResponse(result, status=200)
            except Exception:
                traceback.print_exc()
                response = HttpResponse('{}', status=500)

        response['X_DNC_CSRF'] = new_call_csrf.authorization_token
        
        return response

    def get_urls(self):
        return [
          url("call/", self.view, name="nativecall_call")
        ]

    @property
    def urls(self,):
        return self.get_urls(), 'nativecall', 'nativecall'


registry = Registry()
