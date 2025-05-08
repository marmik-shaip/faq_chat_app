from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, Field, ConfigDict


class ChatHistory(BaseModel):
    id: int = Field(default_factory=int)
    question: str = Field(default_factory=str)
    answer: Optional[str]

class KnowledgeStore(BaseModel):
    id: int
    name: str
    type: str
    documentIds: List[int]
    model_config = ConfigDict(from_attributes=True, extra="ignore")

class QueryRequest(BaseModel):
    id: int
    question: str
    knowledgeStoreList: List[KnowledgeStore]
    historyList: List[ChatHistory] = Field(default_factory=list)

class FileData(BaseModel):
    fileId: int
    fileName: Optional[str] = None
    filePath: str

class DocumentInput(BaseModel):
    id: int
    name: str
    operation: str
    type: str
    data: Optional[List[FileData]] = None


class ResponseHeader(BaseModel):
    success: bool
    code: int
    message: str

class DocumentOutput(BaseModel):
    header: ResponseHeader
    data: Union[dict, List[dict]]

class QueryResponse(BaseModel):
    id: int
    question: str
    answer: str | None
    raw_context: str | None
    knowledgeStoreList: List[KnowledgeStore]


class DocumentOperation(BaseModel):
    id: int
    doc_id: int
    index_id: str
    index_name: str
    operation: str
    file_type: str
    source_path: str
    db_gen_id: str
    created: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")
