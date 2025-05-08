import json
import logging
import os
import urllib.parse
from io import BytesIO

from pydantic import BaseModel

from common.fs_helper import FsHelper
from common.readers import Reader
from common.writers import Writer


class S3File(BaseModel):
    """Holds s3 bucket and prefix"""

    bucket: str
    prefix: str

    @property
    def s3path(self):
        return f"s3://{self.bucket}/{self.prefix}"

    @property
    def s3_path(self):
        return f"s3://{self.bucket}/{self.prefix}"


def get_basename_wo_suffix(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def from_browser_url_to_bucket_prefix(url):
    pi = urllib.parse.urlparse(url)
    bucket = os.path.basename(pi.path)
    query = urllib.parse.parse_qs(pi.query)
    prefix = query['prefix'][0]
    return bucket, prefix


def from_s3_url_to_bucket_prefix(url):
    pi = urllib.parse.urlparse(url)
    bucket = pi.hostname
    prefix = pi.path[1:]
    return bucket, prefix


def get_bucket_prefix(url):
    print(url)
    if url.startswith('s3'):
        return from_s3_url_to_bucket_prefix(url)
    else:
        return from_browser_url_to_bucket_prefix(url)



def get_s3file(url):
    bucket, prefix = get_bucket_prefix(url)
    return S3File(bucket=bucket, prefix=prefix)


class AwsS3Reader(Reader):
    def __init__(self, s3file: S3File, s3, encoding="utf8"):
        self.s3file = s3file
        self.s3 = s3
        self.encoding = encoding

    def read(self) -> str:
        obj = self.s3.ObjectSummary(self.s3file.bucket, self.s3file.prefix)
        result = obj.get()
        return result["Body"].read().decode(self.encoding)


class AwsS3Writer(Writer):
    def __init__(self, s3file: S3File, s3, encoding="utf8"):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.s3file = s3file
        self.s3 = s3
        self.encoding = encoding

    def write(self, text: str):
        obj = self.s3.ObjectSummary(self.s3file.bucket, self.s3file.prefix)
        obj.put(Body=text.encode(self.encoding))


class AwsS3FsHelper(FsHelper):
    def __init__(self, s3, s3_client):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.s3 = s3
        self.s3_client = s3_client

    def exists(self, path_fragment: str):
        self.log.debug("Check if file exists for path_fragment=%s", path_fragment)
        try:
            bucket, prefix = get_bucket_prefix(path_fragment)
            bucket_obj = self.s3.Object(bucket, prefix)
            bucket_obj.load()
            return True
        except:  # pylint: disable=bare-except
            return False

    def get_files(self, path_fragment: str, ext: str):
        self.log.debug("Getting files from path_fragment=%s", path_fragment)
        bucket, prefix = get_bucket_prefix(path_fragment)
        bucket_obj = self.s3.Bucket(bucket)
        return [
            S3File(bucket=s.bucket_name, prefix=s.key)
            for s in bucket_obj.objects.filter(Prefix=prefix.rstrip("/") + "/")
            if s.key.endswith(ext)
        ]

    def get_s3file(self, path_fragment):
        """Get S3File Object from the path_fragment"""

        if isinstance(path_fragment, str):
            bucket, prefix = get_bucket_prefix(path_fragment)
            s3file = S3File(bucket=bucket, prefix=prefix)
        elif isinstance(path_fragment, S3File):
            s3file = path_fragment
        else:
            raise ValueError("path_fragment should be str or S3File")
        return s3file

    def get_bytes(self, path_fragment) -> BytesIO:
        bucket, prefix = get_bucket_prefix(path_fragment)
        obj = self.s3.ObjectSummary(bucket, prefix)
        result = obj.get()
        return BytesIO(result["Body"].read())

    def get_reader(self, path_fragment, encoding=None) -> Reader:
        s3file = self.get_s3file(path_fragment)
        return AwsS3Reader(s3file, self.s3)

    def get_writer(self, path_fragment, encoding=None) -> Writer:
        s3file = self.get_s3file(path_fragment)
        return AwsS3Writer(s3file, self.s3)

    def read_text(self, path_fragment, encoding=None) -> str:
        reader = self.get_reader(path_fragment, encoding)
        return reader.read()

    def read_json(self, path_fragment, encoding=None) -> dict:
        reader = self.get_reader(path_fragment, encoding)
        return json.loads(reader.read())

    def upload_json(self, path_fragment: str, data: dict, encoding="utf8", indent=2):
        writer = self.get_writer(path_fragment=path_fragment, encoding=encoding)
        writer.write(json.dumps(data, indent=indent, ensure_ascii=False))

    def copy(self, from_path, to_path):
        self.log.debug("Copying files from from_path=%s to_path=%s", from_path, to_path)
        from_bucket, from_prefix = get_bucket_prefix(from_path)
        to_bucket, to_prefix = get_bucket_prefix(to_path)

        bucketObj = self.s3.Bucket(to_bucket)
        prefixObj = bucketObj.Object(to_prefix)
        prefixObj.copy({"Bucket": from_bucket, "Key": from_prefix})

    def move(self, from_path, to_path):
        pass

    def download_to(self, from_path, to_local_path, chunk_size=8092):
        self.log.debug("Downloading file %s => %s", from_path, to_local_path)
        bucket, prefix = get_bucket_prefix(from_path)
        print(bucket, prefix)
        obj = self.s3.ObjectSummary(bucket, prefix)
        result = obj.get()
        with open(to_local_path, "wb") as fp:
            data = result["Body"].read(chunk_size)
            while data is not None and len(data) > 0:
                fp.write(data)
                data = result["Body"].read(chunk_size)
        return to_local_path

    def upload_to(self, local_path, to_path):
        self.log.debug("Upload from %s to %s", local_path, to_path)
        bucket, prefix = get_bucket_prefix(to_path)
        with open(local_path, "rb") as fp:
            obj = self.s3.ObjectSummary(bucket, prefix)
            obj.put(Body=fp.read())

    def upload_bytes(self, to_path, data_bytes):
        self.log.debug("Uploading bytes to %s", to_path)
        bucket, prefix = get_bucket_prefix(to_path)
        obj = self.s3.ObjectSummary(bucket, prefix)
        obj.put(Body=data_bytes)

    def delete_file(self, s3_path):
        self.log.debug("Deleting file %s", s3_path)
        bucket, prefix = get_bucket_prefix(s3_path)
        obj = self.s3.Object(bucket, prefix)
        obj.delete()
        self.log.debug("File deleted %s", s3_path)

    def download_folder(self, s3_folder, local_dir):
        bucket_name, prefix = get_bucket_prefix(s3_folder)
        bucket = self.s3.Bucket(bucket_name)

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        if s3_folder and not s3_folder.endswith("/"):
            s3_folder += "/"

        for obj in bucket.objects.filter(Prefix=prefix):
            target_path = os.path.join(local_dir, obj.key[len(prefix) :].lstrip("/"))
            if obj.key.endswith("/"):
                os.makedirs(target_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                bucket.download_file(obj.key, target_path)
                self.log.info(f"Downloaded: {obj.key} → {target_path}")

    def upload_folder(self, s3_folder, local_dir=None):
        bucket_name, prefix = get_bucket_prefix(s3_folder)
        bucket = self.s3.Bucket(bucket_name)

        if s3_folder and not s3_folder.endswith("/"):
            s3_folder += "/"

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_dir)
                s3_path = os.path.join(prefix, relative_path).replace("\\", "/")
                bucket.upload_file(local_file_path, s3_path)

    def delete_folder(self, s3_folder):
        bucket_name, prefix = get_bucket_prefix(s3_folder)
        bucket = self.s3.Bucket(bucket_name)
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        objects_to_delete = [
            {"Key": obj.key} for obj in bucket.objects.filter(Prefix=prefix)
        ]

        if objects_to_delete:
            response = bucket.delete_objects(Delete={"Objects": objects_to_delete})
            self.log.info(
                f"Deleted {len(objects_to_delete)} objects from s3://{bucket_name}/{prefix}"
            )
        else:
            self.log.info(f"No objects found in s3://{bucket_name}/{prefix}")
