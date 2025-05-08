import csv
import json
import os
import urllib.parse


def get_modules_under(directory):
    basedir = os.path.join(os.path.dirname(__file__), "..", directory)
    return [
        f'{directory}.{f.replace(".py", "")}'
        for f in os.listdir(basedir)
        if f.endswith(".py")
    ]


def from_browser_url_to_bucket_prefix(url):
    pi = urllib.parse.urlparse(url)
    bucket = os.path.basename(pi.path)
    query = urllib.parse.parse_qs(pi.query)
    prefix = query["prefix"][0]
    return bucket, prefix


def from_s3_url_to_bucket_prefix(url):
    pi = urllib.parse.urlparse(url)
    bucket = pi.hostname
    prefix = pi.path[1:]
    return bucket, prefix


def get_bucket_prefix(url):
    if url.startswith("s3"):
        return from_s3_url_to_bucket_prefix(url)
    else:
        return from_browser_url_to_bucket_prefix(url)


def get_basename_wo_suffix(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def read_json(filename):
    with open(filename, "r", encoding="utf8") as fp:
        return json.load(fp)


def write_json(filename, data, indent=None, ensure_ascii=False):
    with open(filename, "w", encoding="utf8") as fp:
        json.dump(data, fp, indent=indent, ensure_ascii=ensure_ascii)


def write_csv_rows(filename, data, headers=None):
    if len(data) == 0:
        return

    with open(filename, "w", newline="", encoding="utf8") as fp:
        writer = csv.writer(fp)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def write_csv(filename, rows, headers=None):
    if len(rows) == 0:
        return

    with open(filename, "w", newline="", encoding="utf8") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=headers if headers is not None else rows[0].keys()
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_lines(filename):
    with open(filename, "r", encoding="utf8") as fp:
        return [l.strip() for l in fp.readlines()]


def read_text_file(file_path: str):
    with open(file_path) as fi:
        data = fi.read()

    return data
