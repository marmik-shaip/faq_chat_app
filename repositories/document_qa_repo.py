import logging
from typing import Callable, Optional
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from entities.db_entities import DocumentOperation


class DocumentQADBRepository:
    def __init__(
            self,
            session_factory: Callable[..., AbstractContextManager[Session]],
    ):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session_factory = session_factory

    def get_source_path_by_doc_id(self, doc_id: str) -> Optional[str]:
        self.log.debug(f"Retrieving source path for document ID: {doc_id}")
        try:
            with self.session_factory() as session:
                document_entity = (
                    session.query(DocumentOperation.source_path)
                    .filter(DocumentOperation.doc_id == doc_id)
                    .first()
                )
                if not document_entity:
                    self.log.info(f"No document found with ID: {doc_id}")
                    return None

                return document_entity.source_path

        except Exception as e:
            self.log.error(f"Error retrieving source path for document ID {doc_id}: {str(e)}")
            raise