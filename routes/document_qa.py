import os

from dotenv import load_dotenv
from fastapi import APIRouter

from commands.document_service import DocumentService, DocChatService
from entities.server_entities import (
    DocumentInput,
    DocumentOutput,
    ResponseHeader,
    QueryRequest,
    QueryResponse,
)

load_dotenv(".env")

router = APIRouter()

SAVE_DIR = "downloaded_docs"
os.makedirs(SAVE_DIR, exist_ok=True)


def get_code_message(response):
    code = 200 if response else 404
    message = "Success" if response else "Failed"
    return code, message



@router.post("/document/qa", tags=["Document Q&A"])
def document_qa_service(document: DocumentInput) -> DocumentOutput:
    print(document)
    response = None
    if document.operation.lower() in ["add", "update", "upload"]:
        response = DocumentService().upload_input_docs(
            str(document.id),
            document.name,
            document.operation,
            document.type,
            document.data,
        )
    elif document.operation.lower() == "delete":
        if document.data:
            response = DocumentService().delete_docs(str(document.id), document.data)
        else:
            response = DocumentService().delete_index(str(document.id))
    code = 200 if response else 0
    message = f"{document.operation} {'successful' if response else 'failed'}."
    print(response, code, message)
    return DocumentOutput(
        header=ResponseHeader(success=response, code=code, message=message), data={}
    )


@router.post("/document/doc_chat", tags=["Document Q&A"])
def doc_chat_service(
    query: QueryRequest,
) -> QueryResponse:
    print(query)
    response = DocChatService().document_chat(query)
    print(response)
    return response
