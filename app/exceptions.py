import traceback


def get_traceback(exception):
    return [y for x in
            traceback.format_exception(type(exception), exception, exception.__traceback__)
            for y in x.split("\n") if y != ""]


class BaseApiError(Exception):
    # message = ""

    def __init__(self):
        if len(self.args) > 0:
            args = {x: self.args[i] for i, x in enumerate(self.__init__.__code__.co_varnames[1:])}
            self.__dict__.update(args)
        # Exception.__init__(self, self.message)
        Exception.__init__(self)


class InternalError(BaseApiError):
    pass


class CannotAppendTaskToQueue(BaseApiError):
    pass


class CannotFetchTaskFromQueue(BaseApiError):
    pass


class FetchedTaskIsNull(BaseApiError):
    pass


class TaskTimeout(BaseApiError):
    pass


# DE LA ENTRADAS AL PROCESO
class NoAttributeError(BaseApiError, AttributeError):
    message = "No se ha proveido un argumento"

    def __init__(self, param_name):
        super().__init__()


class InvalidValueError(BaseApiError, ValueError):
    message = "Se ha proveido un valor invalido para el argumento"

    def __init__(self, param_name, value):
        super().__init__()


class EmptyValueError(BaseApiError, ValueError):
    message = "Se ha proveido un valor vacio para el argumento"

    def __init__(self, param_name, value):
        super().__init__()
