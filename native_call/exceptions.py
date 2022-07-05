
class NotValidateException(Exception):
    pass


class FunctionAlreadyRegisteredException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class ForbiddenException(Exception):
    pass


class InvalidRegistrationException(Exception):
    pass


class InvalidParameterTypeError(Exception):
    pass


class ErroResponse(Exception):
    def __init__(self, message, status_code=400, **kwargs):
        super(ErroResponse, self).__init__(message, **kwargs)
        self.message = message
        self.status_code = status_code