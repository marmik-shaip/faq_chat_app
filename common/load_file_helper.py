import base64
import os
import platform
import subprocess
from collections.abc import Iterator
from io import BytesIO
from pathlib import Path

import chardet
import magic
import pymupdf
from PIL import Image
from langchain_core.messages import HumanMessage


def image_bytes_to_msgs(file_bytes):
    image_data = base64.b64encode(file_bytes).decode("utf8")
    mime_type = magic.from_buffer(file_bytes, mime=True)
    # print('Mime Type', mime_type)
    image_url = f"data:{mime_type};base64,{image_data}"
    return {
        "type": "image_url",
        "image_url": {"url": image_url},
    }


def load_image(filename):
    with open(filename, "rb") as fp:
        return HumanMessage(content=[image_bytes_to_msgs(fp.read())])


def get_page_images(fp, filetype) -> Iterator[tuple[int, Image.Image]]:
    print(fp, filetype)
    doc = pymupdf.open(stream=fp, filetype=filetype)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        zoom_x = 2.0
        zoom_y = 2.0
        mat = pymupdf.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        yield page_num, img


def get_bytes(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return buffered.getvalue()


def load_pdf(pdffile, pages=None):
    print("File is ", pdffile)
    with open(pdffile, "rb") as fp:
        return HumanMessage(
            content=[
                image_bytes_to_msgs(get_bytes(img))
                for page, img in get_page_images(BytesIO(fp.read()), "pdf")
                if pages is None or page in pages
            ]
        )

def load_txt(txtfile):
    with open(txtfile, "rb") as fp:
        data = fp.read()
        enc = chardet.detect(data)
        return HumanMessage(content=[data.decode(enc["encoding"])])


def load_csv(csvfile):
    return load_txt(csvfile)


def load_file(filename):
    print(f"File Name : {filename}")
    parts = os.path.splitext(filename)
    if len(parts) == 1:
        raise RuntimeError("Error file-type unknown")
    ext = parts[1].lower()
    if ext == ".pdf":
        return load_pdf(filename)
    elif ext in {".docx", ".doc"}:
        pdf_file = docx_to_pdf(filename)
        print(f"PDF File : {pdf_file}")
        return load_pdf(pdf_file)
    elif ext == ".txt":
        return load_txt(filename)
    elif ext == ".csv":
        return load_csv(filename)
    elif ext in {".jpeg", ".jpg", ".png"}:
        return load_image(filename)
    else:
        raise RuntimeError(f"Error unknown file extension {ext}")


def run_for_windows_system(file_path, new_pdf_path):
    try:
        import win32com.client

        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False

        doc = word.Documents.Open(str(file_path.absolute()))
        doc.SaveAs(str(new_pdf_path), FileFormat=17)  # 17 is the PDF format
        doc.Close()
        word.Quit()
    except Exception as e:
        raise Exception(f"PDF conversion failed on Windows: {str(e)}")


def run_for_ubuntu_system(file_path, new_pdf_path, pdf_dir, system):
    try:
        subprocess.run(
            ["unoconv", "-f", "pdf", "-o", str(new_pdf_path), str(file_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            subprocess.run(
                [
                    "/usr/bin/libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(pdf_dir),
                    str(file_path),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            raise Exception(
                f"PDF conversion failed on {system}: {str(e)}. Please install unoconv or LibreOffice."
            )


def docx_to_pdf(doc_path):
    file_path = Path(doc_path)
    new_pdf_path = os.path.join(
        "converted_doc_pdf_files", os.path.splitext(doc_path)[0] + ".pdf"
    )

    system = platform.system()

    if system == "Windows":
        run_for_windows_system(file_path, new_pdf_path)
    elif system in ["Linux", "Darwin"]:
        run_for_ubuntu_system(
            file_path, new_pdf_path, os.path.dirname(doc_path), system
        )
    else:
        raise Exception(f"Unsupported operating system: {system}")

    if not os.path.exists(new_pdf_path):
        raise Exception(
            f"PDF conversion failed: Output file not found at {new_pdf_path}"
        )
    return new_pdf_path
