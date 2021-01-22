import os

from sklearn.pipeline import Pipeline

from processor.pageclass import PageClass
import pickle

_classifier: Pipeline = None


def load_obj():
    global _classifier
    if _classifier is None:
        pickled_obj_path = os.environ["DEFAULT_PAGECLASSIFIERPATH"]
        with open(pickled_obj_path, "rb") as file:
            _classifier = pickle.load(file)


def predict_with_proba(page_text):
    """
    Predice la probabilidad de un texto frente a los tipos de PageClass

    Args:
        page_text:

    Returns:
    Lista de tuplas PageClass-Probabilidad ordenadas de forma descendente
    """
    load_obj()
    probs = _classifier.predict_proba([page_text])[0]
    classes = [PageClass.from_value(x) for x in _classifier.classes_]
    class_probs = list(zip(classes, probs))
    class_probs.sort(key=lambda x: x[1], reverse=True)
    return class_probs
