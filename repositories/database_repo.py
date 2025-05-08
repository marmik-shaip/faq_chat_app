import logging
from contextlib import AbstractContextManager
from idlelib.calltip_w import CalltipWindow
from typing import Callable

from sqlalchemy.orm import Session

from entities.db_entities import Users, Projects, user_project_association, Documents


class UsersDBRepo:
    def __init__(self,
                 session_factory: Callable[..., AbstractContextManager[Session]]
                 ) -> None:
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session_factory = session_factory

    def get_user_by_id(self, user_id: int):
        with self.session_factory() as session:
            instance = (
                session.query(Users)
                .filter(Users.user_id == user_id)
                .first()
            )
            if instance is None:
                raise RuntimeError(
                    f"User not found user_id={user_id}"
                )
            return instance

    def allow_project_to_user(self, user_id: int, project_id: int):
        with self.session_factory() as session:
            user = self.get_user_by_id(user_id)
            user.projects.append(project_id)
            session.commit()

    def add_user(self, user_id: int, username: str):
        with self.session_factory() as session:
            instance = Users(
                user_id=user_id,
                username=username
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def remove_user(self, user_id: int):
        with self.session_factory() as session:
            session.query(Users).filter(Users.user_id == user_id).delete()
            session.commit()

    def deny_project_to_user(self, user_id: int, project_id: int):
        with self.session_factory() as session:
            user = self.get_user_by_id(user_id)
            user.projects.remove(project_id)
            session.commit()

    def is_user_allowed(self, session, user_id: int, project_id: int) -> bool:
        with self.session_factory() as session:
            # Query the association table directly for better performance
            result = session.query(user_project_association).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            return result is not None

    def get_user_by_username(self, username: str):
        with self.session_factory() as session:
            instance = (
                session.query(Users)
                .filter(Users.username == username)
                .first()
            )
            if instance is None:
                return None
            return instance


class ProjectsDBRepo:
    def __init__(self,
                 session_factory: Callable[..., AbstractContextManager[Session]]
                 ) -> None:
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session_factory = session_factory

    def get_project_by_id(self, project_id: int):
        with self.session_factory() as session:
            instance = (
                session.query(Projects)
                .filter(Projects.project_id == project_id)
                .first()
            )
            if instance is None:
                raise RuntimeError(
                    f"Project not found project_id={project_id}"
                )
            return instance

    def get_allowed_users_for_project(self, project_id: int):
        with self.session_factory() as session:
            project = self.get_project_by_id(project_id)
            return project.users

    def add_project(self, project_id: int, project_name: str):
        with self.session_factory() as session:
            instance = Projects(
                project_id=project_id,
                project_name=project_name
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def remove_project(self, project_id: int):
        with self.session_factory() as session:
            session.query(Projects).filter(Projects.project_id == project_id).delete()
            session.commit()


class DocumentDBRepo:
    def __init__(self,
                 session_factory: Callable[..., AbstractContextManager[Session]]
                 ) -> None:
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session_factory = session_factory

    def get_documents_by_project_id(self, doc_id: int):
        with self.session_factory() as session:
            instances = (
                session.query(Documents)
                .filter(Documents.project_id == doc_id)
                .all()
            )
            if instances is None:
                raise RuntimeError(
                    f"Documents not found project_id={doc_id}"
                )
            return instances

    def add_document(self, project_id: int, doc_name: str, document_path: str):
        with self.session_factory() as session:
            instance = Documents(
                project_id=project_id,
                doc_name=doc_name,
                doc_path=document_path
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def remove_document(self, doc_id: int):
        with self.session_factory() as session:
            session.query(Documents).filter(Documents.doc_id == doc_id).delete()
            session.commit()

    def remove_document_by_project_id(self, project_id: int):
        with self.session_factory() as session:
            session.query(Documents).filter(Documents.project_id == project_id).delete()
            session.commit()

    def add_documents(self, project_id: int, document_dict: dict):
        with self.session_factory() as session:
            for doc_name, document_path in document_dict.items():
                instance = Documents(
                    project_id=project_id,
                    doc_name=doc_name,
                    doc_path=document_path
                )
                session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance