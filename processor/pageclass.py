from enum import Enum


class PageClass(Enum):
    # CUENTA POR PAGAR
    CP = "CP"
    # FACTURA
    FA = "FA"
    # ORDEN DE COMPRA LOGISTICA
    OC_LOG = "OC.LOG"
    # ORDEN DE COMPRA CONTABILIDAD
    OC_CON = "OC.CON"
    # PARTE DE INGRESO
    PI = "PI"
    # ACTA DE CONFORMIDAD
    AC = "AC"
    # Sustento
    ST = "ST"
    # ACTA DIRECTORIO
    AD = "AD"

    @staticmethod
    def from_value(value):
        value_to_enum = {x.value: x for x in list(PageClass)}
        return value_to_enum[value]