import regex

from app import exceptions
from processor import processor2

import os
import tempfile
import base64


class File:
    def __init__(self, filepath, filename=''):
        self.filepath = filepath
        self.origfilename = filename


class FileView:
    def __init__(self, _json: dict):

        def validate_and_get_field(field_name, pattern=None):
            if field_name not in _json:
                raise exceptions.NoAttributeError(field_name)
            if type(_json[field_name]) != str or not _json[field_name] or \
                    (pattern and not regex.match(pattern, _json[field_name])):
                raise exceptions.InvalidValueError(field_name, _json[field_name])
            return _json[field_name]

        self.filebase64 = validate_and_get_field("filebase64")
        self.filename = validate_and_get_field("filename", r"^[\w,\s-]+\.[A-Za-z]{3,4}$")
        self.id = validate_and_get_field("id")
        self.filepath = None

    def write_in(self, dir_path):
        extension = os.path.splitext(self.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False, dir=dir_path) as tf:
            _bytes = base64.b64decode(self.filebase64)
            tf.write(_bytes)
        self.filepath = tf.name


class TaskInput:
    def __init__(self, _json):
        if "doc_type" not in _json:
            raise exceptions.NoAttributeError("doc_type")
        if _json["doc_type"] not in [x.value for x in processor2.DocType]:
            raise exceptions.InvalidValueError("doc_type", _json["doc_type"])

        if "extract_meta" in _json and type(_json["extract_meta"]) != bool:
            raise exceptions.InvalidValueError("extract_meta", _json["extract_meta"])

        if "files" not in _json:
            raise exceptions.NoAttributeError("files")
        if type(_json["files"]) != list:
            raise exceptions.InvalidValueError("files", _json["files"])
        if len(_json["files"]) == 0:
            raise exceptions.EmptyValueError("files", _json["files"])

        self.doc_type = "self.doc_type" #s processor2.DocType.from_value(_json["doc_type"])
        self.extract_meta = "self.extract_meta" #s _json.get("extract_meta", False)
        self.files = _json["files"] #s [FileView(x) for x in _json["files"]]

    def write_files(self, dir_path):
        for f in self.files:
            f.write_in(dir_path)
