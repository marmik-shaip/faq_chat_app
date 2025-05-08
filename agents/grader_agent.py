from dependency_injector.wiring import Provide
from langchain_core.prompts import (
    PromptTemplate,
)
from langchain_openai import ChatOpenAI

from agents.agent_states import GradeLLMResponse
from container import Container
from repositories.chroma_db_repo import DocRepository


class GraderNode:
    def __init__(
        self,
        model="gpt-4o-mini",
        db: DocRepository = Provide[Container.doc_repo],
    ):
        prompt = PromptTemplate.from_template(
            db.get_prompt_by_prompt_name("Grader Agent Prompt")
        )
        llm = ChatOpenAI(model=model, temperature=0.0).with_structured_output(
            GradeLLMResponse
        )
        self.chain = prompt | llm

    def __call__(self, query, llm_response):
        inputs = {"query": query, "llm_response": llm_response}
        result = self.chain.invoke(inputs)
        return result
