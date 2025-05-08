import shutil
from glob import glob

from common.readers import LocalFileReader, Reader
from common.writers import LocalFileWriter, Writer


class FsHelper:
    def get_files(self, path_fragment:str, ext:str):
        raise NotImplementedError()

    def get_reader(self, path_fragment, encoding=None) -> Reader:
        raise NotImplementedError()

    def get_writer(self, path_fragment, encoding=None) -> Writer:
        raise NotImplementedError()

    def copy(self, from_path, to_path):
        raise NotImplementedError()

    def move(self, from_path, to_path):
        raise NotImplementedError()

    def download_to(self, from_path, to_local_path):
        raise NotImplementedError()

    def upload_to(self, local_path, to_path):
        raise NotImplementedError()
    
    def upload_bytes(self, to_path, data_bytes):
        raise NotImplementedError()


class LocalFsHelper(FsHelper):
    def get_files(self, path_fragment: str, ext: str):
        return list(glob(f'{path_fragment}/**/*.{ext}', recursive=True))

    def get_reader(self, path_fragment, encoding=None):
        return LocalFileReader(path_fragment, encoding)

    def get_writer(self, path_fragment, encoding=None):
        return LocalFileWriter(path_fragment, encoding)
    
    def copy(self, from_path, to_path):
        shutil.copy(from_path, to_path)

    def move(self, from_path, to_path):
        shutil.copy(from_path, to_path)
    
    def download_to(self, from_path, to_local_path):
        return self.copy(from_path, to_local_path)

    def upload_to(self, local_path, to_path):
        return self.copy(local_path, to_path)
    
    def upload_bytes(self, to_path, data_bytes):
        writer = LocalFileWriter(to_path)
        writer.write(data_bytes)
