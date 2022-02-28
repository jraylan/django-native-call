from asyncio import get_event_loop
import inspect

from native_call.exceptions import InvalidParameterTypeError


class WrappedFunction:

    def __init__(self, func, name, arg_types, permissions, allow_anonymous):
        self.func = func
        self.name = name
        self.arg_types = arg_types or []
        self.permissions = permissions or []
        self.allow_anonymous = allow_anonymous

    def __call__executor__(self, *args):
        if inspect.iscoroutinefunction(self.func):
            from .utils import async_to_sync
            return async_to_sync(self.func)(*args)
        return self.func(*args)

    def __call__(self, *args):
        try:
            get_event_loop()
        except RuntimeError:
            return self.__call__executor__(*args)
        else:
            from .utils import database_sync_to_async
            return self.__call__executor__(*args)

    def validate(self, user, params=None):
        if params:
            for i, arg in enumerate(self.arg_types):
                try:
                    params[i] = arg[i](params[i])
                except ValueError:
                    raise InvalidParameterTypeError(
                        'Sent parameter "{} must be of type {}'.format(
                            params[i],
                            arg[i].__name__
                        )
                    )
                except IndexError:
                    raise InvalidParameterTypeError(
                        '"{}" requires at least {} args. {} was given'.format(
                            self.name,
                            len(self.arg_types),
                            len(params)
                        )
                    )

        if not self.allow_anonymous and user.is_anonymous:
            return False

        if self.permissions:
            return user.has_perms(self.permissions)

        return True
