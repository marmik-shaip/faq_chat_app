"""Reader for Files"""
from typing import List
import logging
import csv
import json
import io
import chardet
from pydantic import BaseModel


class Reader:
    """Abstract class for the reader"""

    def read(self) -> str:
        """Reads the text"""
        raise NotImplementedError()


class LocalFileReader(Reader):
    def __init__(self, filepath: str, encoding=None):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.filepath = filepath
        self.encoding = encoding

    def detect_encoding(self):
        with open(self.filepath, 'rb') as fp:
            encoding = chardet.detect(fp.read())
            self.encoding = encoding['encoding']

    def read(self) -> str:
        if self.encoding is None:
            self.detect_encoding()
        self.log.info('Detected Encoding: %s', self.encoding)
        with open(self.filepath, 'r', encoding=self.encoding) as fp:
            return fp.read()


class CsvReader:
    def __init__(self, reader):
        self.reader = reader

    def get_rows(self) -> str:
        fp = io.StringIO(self.reader.read())
        return list(csv.DictReader(fp))

    def get_model(self, model: BaseModel) -> List[BaseModel]:
        rows = self.get_rows()
        return [model.model_validate(row) for row in rows]


class JsonReader:
    def __init__(self, reader):
        self.reader = reader

    def get_json(self) -> str:
        return json.loads(self.reader.read())
