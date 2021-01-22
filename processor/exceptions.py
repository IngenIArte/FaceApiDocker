class BaseJockeyProcessorError(Exception):

    def __init__(self):
        if len(self.args) > 0:
            args = {x: self.args[i] for i, x in enumerate(self.__init__.__code__.co_varnames[1:])}
            self.__dict__.update(args)
        Exception.__init__(self)


# Acta - Error de validacion
class EmptyOCRResultError(BaseJockeyProcessorError):
    """Sin texto reconocido por OCR"""


# Acta - Errores de extraccion de fecha
class DatePatternError(BaseJockeyProcessorError):
    """El texto no cumple el patron regex para la fecha"""
    pass


class MonthNameError(BaseJockeyProcessorError):
    """El nombre del mes no aparece en el listado de meses"""

    def __init__(self, month_name):
        super().__init__()


# Acta - Errores de extraccion de razon social
class JockeyAPITimeout(BaseJockeyProcessorError):
    """Tiempo de espera del servicio excedido"""


class JockeyAPIError(BaseJockeyProcessorError):
    """Problema de comunicacion"""


class LowSimilarityError(BaseJockeyProcessorError):
    """No se encontro la empresa por baja similitud"""


class FormatError(BaseJockeyProcessorError):
    """El texto no tiene el formato esperado"""

    def __init__(self, expected_format):
        super().__init__()
