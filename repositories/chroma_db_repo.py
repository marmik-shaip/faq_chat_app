import logging
import os
import traceback
from contextlib import AbstractContextManager
from typing import Callable, List

import chromadb
from chromadb import Settings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session

from entities import db_entities, server_entities

load_dotenv(".env")

llama_embeddings = OllamaEmbeddings(model="llama3.2")
openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=3072)


def sanitize_index_id(index_id: str) -> str:
    # fallback name if invalid
    if not isinstance(index_id, str) or len(index_id) < 3:
        return "default_index"
    return index_id

class DocRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        persist_directory: str = "./chroma_db",
    ):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session_factory = session_factory
        self.persist_directory = persist_directory

        self.chroma_client = chromadb.PersistentClient(self.persist_directory)

        # .HttpClient(
        #     host="10.142.152.101",
        #     port=8000,
        #     ssl=False,
        #     settings=Settings(allow_reset=True, anonymized_telemetry=False),
        # ))

    def get_or_create_collection(self, index_name: str):
        try:
            vector_store = Chroma(
                collection_name=index_name,
                embedding_function=openai_embeddings,
                persist_directory=self.persist_directory,
                client=self.chroma_client,
            )

            self.log.info(f"Using existing collection '{index_name}'")
            return vector_store

        except Exception as e:
            self.log.info(f"Creating new collection '{index_name}'")
            vector_store = Chroma.from_documents(
                documents=[],
                embedding=openai_embeddings,
                persist_directory=self.persist_directory,
                collection_name=index_name,
                client=self.chroma_client,
            )
            return vector_store

    def get_all_docs(self, index_name: str):
        try:
            collection = self.chroma_client.get_collection(index_name)
            results = collection.get()
            documents = [
                {"id": doc_id, "text": doc_text, "metadata": meta}
                for doc_id, doc_text, meta in zip(
                    results["ids"], results["documents"], results["metadatas"]
                )
            ]

            self.log.info(f"From {index_name} all documents are fetched.")
            return documents
        except:
            self.log.info(f"Failed to list document of {index_name} collection.")
            return []

    def upload_document(
        self,
        s3_path: str,
        doc_id: int,
        index_id: str,
        index_name: str,
        operation: str,
        file_type: str,
        doc_chunks: List,
    ):
        vector_store = self.get_or_create_collection(index_id)
        db_id_lst = vector_store.add_documents(doc_chunks)

        db_id_lst = ",".join(db_id_lst)

        with self.session_factory() as session:
            document = db_entities.DocumentOperation(
                doc_id=doc_id,
                index_id=index_id,
                index_name=index_name,
                operation=operation,
                file_type=file_type,
                source_path=s3_path,
                db_gen_id=db_id_lst,
            )
            session.add(document)
            session.commit()
            session.refresh(document)

            self.log.info(
                f"Document '{os.path.basename(document.source_path)}' uploaded to '{index_id}' collection and database."
            )
            uploaded_data = server_entities.DocumentOperation.model_validate(document)

        return uploaded_data.db_gen_id

    def delete_by_id(self, doc_id: int, index_id: str):
        collection = self.chroma_client.get_or_create_collection(index_id)
        with self.session_factory() as session:
            document = (
                session.query(db_entities.DocumentOperation)
                .filter(db_entities.DocumentOperation.doc_id == doc_id)
                .first()
            )

            if document:
                db_gen_id_lst = document.db_gen_id.split(",")
                collection.delete(ids=db_gen_id_lst)

                session.query(db_entities.DocumentOperation).filter(
                    db_entities.DocumentOperation.doc_id == doc_id
                ).delete(synchronize_session="fetch")
                session.commit()

                self.log.info(
                    f"Document '{os.path.basename(document.source_path)}' deleted from '{index_id}' collection and database."
                )
        return True

    def delete_index(self, index_id: str):

        try:
            self.chroma_client.delete_collection(index_id)

            with self.session_factory() as session:
                session.query(db_entities.DocumentOperation).filter(
                    db_entities.DocumentOperation.index_id == index_id
                ).delete(synchronize_session=False)
                session.commit()

                self.log.info(
                    f"Collection '{index_id}' and all the documents are deleted from database."
                )
        except Exception as e:
            self.log.warning(f"Collection '{index_id}' deletion failed: {str(e)}")

        return True

    def get_prompt_by_prompt_name(self, promptName: str):
        try:
            with self.session_factory() as session:
                document = (
                    session.query(db_entities.Prompts)
                    .filter(db_entities.Prompts.prompt_name == promptName)
                    .first()
                )

                return document.prompt if document else ""

        except Exception as e:
            self.log.error(
                "Exception in get_prompt_by_prompt_name: %s", traceback.format_exc()
            )
            return ""

    def get_json_template_by_id(self, temp_id: str):
        try:
            with self.session_factory() as session:
                json_template = (
                    session.query(db_entities.JsonTemplates)
                    .filter(db_entities.JsonTemplates.id == temp_id)
                    .first()
                )

                return json_template.template if json_template else ""

        except Exception as e:
            self.log.error(
                "Exception in get_json_template_by_id: %s", traceback.format_exc()
            )
            return ""

    def get_json_template_all(self) -> List:
        try:
            with self.session_factory() as session:
                json_template_lst = (
                    session.query(db_entities.JsonTemplates)
                    .all()
                )

                return json_template_lst

        except Exception as e:
            self.log.error(
                "Exception in get_json_template_all: %s", traceback.format_exc()
            )
            return []
