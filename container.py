import logging.config
import os

import boto3
import openai
from botocore.config import Config
from dependency_injector import containers, providers
from langchain_openai import ChatOpenAI

from common.aws_fs_helper import AwsS3FsHelper
from common.aws_textract import AwsTextract
from repositories.chroma_db_repo import DocRepository
from repositories.database_repo import UsersDBRepo
from repositories.document_qa_repo import DocumentQADBRepository
from services.databases import Database

FILE_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG = os.path.join(FILE_DIR, "./configs/config.yml")
LOGGING_FILE = os.path.join(FILE_DIR, "./configs/logging.ini")


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=[DEFAULT_CONFIG])

    logging = providers.Resource(logging.config.fileConfig, fname=LOGGING_FILE)

    print(config.db)
    db_session = providers.Singleton(Database, db_config=config.db)



    session = providers.ThreadLocalSingleton(boto3.session.Session)

    s3 = providers.ThreadLocalSingleton(
        session.provided.resource.call(), service_name="s3"
    )

    s3_client_transcribe = providers.ThreadLocalSingleton(
        session.provided.client.call(),
        service_name="transcribe",
        region_name="us-east-1",
    )

    textract_client = providers.ThreadLocalSingleton(
        session.provided.client.call(), service_name="textract"
    )

    s3_config = Config(s3={"use_accelerate_endpoint": True})
    s3_client = providers.ThreadLocalSingleton(
        session.provided.client.call(), service_name="s3", config=s3_config
    )

    s3_helper = providers.ThreadLocalSingleton(
        AwsS3FsHelper, s3=s3, s3_client=s3_client
    )

    sqs_client = providers.ThreadLocalSingleton(
        session.provided.client.call(), service_name="sqs"
    )

    openai_client = providers.ThreadLocalSingleton(openai.OpenAI)

    doc_repo = providers.ThreadLocalSingleton(
        DocRepository, session_factory=db_session.provided.session
    )

    user_repo = providers.ThreadLocalSingleton(
        UsersDBRepo, session_factory=db_session.provided.session
    )

    document_qa_repo = providers.ThreadLocalSingleton(
        DocumentQADBRepository, session_factory=db_session.provided.session
    )

    gpt_4o_mini_chat_llm = providers.ThreadLocalSingleton(
        ChatOpenAI(model="gpt-4o-mini", temperature=0)
    )

    llm = providers.ThreadLocalSingleton(ChatOpenAI(model="gpt-4o-mini", temperature=0))

    aws_text_tract = providers.ThreadLocalSingleton(AwsTextract, client=textract_client)

