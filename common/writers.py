"""Writer for Files"""
import os


class Writer:
    """Abstract class for the writer"""

    def write(self, text: str):
        """Writes the text to file"""
        raise NotImplementedError()


class LocalFileWriter(Writer):
    def __init__(self, filepath: str, encoding='utf8'):
        self.filepath = filepath
        self.encoding = encoding

    def write(self, text: str, encoding=None) -> str:
        dirpath = os.path.dirname(self.filepath)
        os.makedirs(dirpath, exist_ok=True)
        with open(self.filepath, 'w', encoding=encoding if encoding else self.encoding) as fp:
            fp.write(text)
