import processor.exceptions
import app.exceptions

messages = {
    Exception: "Ocurrio un error inesperado.",
    app.exceptions.InternalError: "Error interno",
    processor.exceptions.EmptyOCRResultError: "No hubo ningun resultado del OCR.",
    processor.exceptions.MonthNameError: "No se reconoció el texto como un mes.",
    processor.exceptions.DatePatternError: "No se encontro el patron '(dia) de (mes) de (año)'.",
    processor.exceptions.JockeyAPITimeout: "Se excedio el tiempo de espera del servicio.",
    processor.exceptions.JockeyAPIError: "Ocurrio un problema de comunicacion con el servicio,",
    processor.exceptions.LowSimilarityError: "No se encontro coincidencia entre la lista de empresas y el contenido "
                                             "del documento.",
    processor.exceptions.FormatError: "No se encontro texto con el formato esperado: '{expected_format}'",
}
