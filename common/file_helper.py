import base64
from collections.abc import Iterator
import os
from PIL import Image
from io import BytesIO
import chardet
import magic

import pymupdf
from langchain_core.messages import HumanMessage


def image_bytes_to_msgs(file_bytes):
    image_data = base64.b64encode(file_bytes).decode('utf8')
    mime_type = magic.from_buffer(file_bytes, mime=True)
    # print('Mime Type', mime_type)
    image_url = f"data:{mime_type};base64,{image_data}"
    return {
        'type': 'image_url',
        'image_url': {'url': image_url},
    }


def load_image(filename):
    with open(filename, 'rb') as fp:
        return HumanMessage(content=[image_bytes_to_msgs(fp.read())])


def load_image_fp(fp):
    return HumanMessage(content=[image_bytes_to_msgs(fp.read())])


def get_page_images(fp, filetype) -> Iterator[tuple[int, Image.Image]]:
    doc = pymupdf.open(stream=fp, filetype=filetype)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        zoom_x = 2.0
        zoom_y = 2.0
        mat = pymupdf.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        yield page_num, img


def get_bytes(img):
    buffered = BytesIO()
    img.save(buffered, format='JPEG')
    return buffered.getvalue()


def load_pdf(pdffile, pages=None):
    with open(pdffile, 'rb') as fp:
        return HumanMessage(
            content=[
                image_bytes_to_msgs(get_bytes(img))
                for page, img in get_page_images(BytesIO(fp.read()), 'pdf')
                if pages is None or page in pages
            ]
        )


def load_pdf_fp(fp):
    return HumanMessage(
        content=[
            image_bytes_to_msgs(get_bytes(img))
            for page, img in get_page_images(BytesIO(fp.read()), 'pdf')
        ]
    )


def load_txt(txtfile):
    with open(txtfile, 'rb') as fp:
        data = fp.read()
        enc = chardet.detect(data)
        return HumanMessage(content=data.decode(enc['encoding']))


def load_txt_fp(fp):
    data = fp.read()
    enc = chardet.detect(data)
    return HumanMessage(content=data.decode(enc['encoding']))


def load_csv(csvfile):
    return load_txt(csvfile)


def load_file(filename):
    parts = os.path.splitext(filename)
    if len(parts) == 1:
        raise RuntimeError('Error file-type unknown')
    if parts[1] == '.pdf':
        return load_pdf(filename)
    elif parts[1] == '.txt':
        return load_txt(filename)
    elif parts[1] == '.csv':
        return load_csv(filename)
    elif parts[1] in {'.jpeg', '.jpg', '.png'}:
        return load_image(filename)
    else:
        raise RuntimeError(f'Error unknown file extension {parts[1]}')
