import os

import boto3
from common.aws_fs_helper import from_s3_url_to_bucket_prefix
from common.aws_textract import AwsTextract


session = boto3.session.Session()
textract_client = session.client("textract")
aws_text_tract = AwsTextract(textract_client)

def read_pdf(s3_pdf_path: str):
    bucket, prefix = from_s3_url_to_bucket_prefix(s3_pdf_path)
    textract_output = aws_text_tract.transcribe_document(
        bucket, prefix
    )

    content_by_pages = []
    for pages in textract_output:
        lst = ["" for i in range(pages["DocumentMetadata"]["Pages"])]
        for block in pages["Blocks"]:
            if block["BlockType"] == "LINE":
                lst[block["Page"] - 1] += f'{block["Text"]} \n'
        content_by_pages.extend(lst)

    return "\n".join(content_by_pages)