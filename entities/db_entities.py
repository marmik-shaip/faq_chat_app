from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Table, VARCHAR, Text
from sqlalchemy.orm import relationship

from services import databases

# Association table to link users and projects (many-to-many relationship)
user_project_association = Table(
    "user_project_association",
    databases.Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id")),
    Column("project_id", Integer, ForeignKey("projects.project_id"))
)


class DocumentOperation(databases.Base):
    __tablename__ = "document_operations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer)
    index_id = Column(VARCHAR(10))
    index_name = Column(Text)
    operation = Column(Text)
    file_type = Column(Text)
    source_path = Column(Text)
    db_gen_id = Column(Text)
    created = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        fields = [
            f"id={self.id}",
            f"index_id={self.index_id}",
            f"index_name={self.index_name}",
            f"operation={self.operation}",
            f"file_type={self.file_type}",
            f"doc_id={self.doc_id}",
            f"source_path={self.source_path}",
            f"db_gen_id={self.db_gen_id}",
            f"created={self.created}",
        ]
        return f'DocumentOperation({",".join(fields)})'


# Projects Table
class Projects(databases.Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    # One-to-many relationship: A project has many documents
    documents = relationship("Documents", back_populates="project")

    # Many-to-many relationship: Users associated with the project
    users = relationship("Users", secondary=user_project_association, back_populates="projects")


# Documents Table
class Documents(databases.Base):
    __tablename__ = "documents"

    doc_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    doc_name = Column(String(255), nullable=False)
    doc_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Many-to-one relationship: A document belongs to a project
    project = relationship("Projects", back_populates="documents")


# Users Table
class Users(databases.Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    # Many-to-many relationship: Projects associated with the user
    projects = relationship("Projects", secondary=user_project_association, back_populates="users")

class Prompts(databases.Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_name = Column(Text)
    prompt = Column(Text)

    def __repr__(self):
        fields = [
            f"id={self.id}",
            f"prompt_name={self.prompt_name}",
            f"prompt={self.prompt}",
        ]
        return f'Prompts({",".join(fields)})'


# Function to check if a user is allowed to use a given project_id
def is_user_allowed(session, user_id: int, project_id: int) -> bool:
    # Query the association table directly for better performance
    result = session.query(user_project_association).filter_by(
        user_id=user_id,
        project_id=project_id
    ).first()
    return result is not None


# Function to get all documents for a given project if the user is allowed
def get_documents_for_project(session, user_id: int, project_id: int):
    if not is_user_allowed(session, user_id, project_id):
        return "Access Denied"

    # Fetch all documents for the given project
    documents = session.query(Documents).filter(Documents.project_id == project_id).all()
    return documents
