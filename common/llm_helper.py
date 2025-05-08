from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


class StructuredLLM:
    def __init__(self, prompt, klass, model='gpt-4o-mini', temperature=0.0):
        if model.startswith('gpt'):
            llm = ChatOpenAI(model=model, temperature=temperature)
        elif model.startswith('o3'):
            llm = ChatOpenAI(model=model)
        else:
            llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)

        self.chain = prompt | llm.with_structured_output(klass)

    def __call__(self, inputs):
        return self.chain.invoke(inputs)


class SimpleLLM:
    def __init__(self, prompt_text, model='gpt-4o-mini', temperature=0.0):
        prompt = (
            PromptTemplate.from_template(prompt_text)
            if isinstance(prompt_text, str)
            else prompt_text
        )
        if model.startswith('gpt'):
            llm = ChatOpenAI(model=model, temperature=temperature)
        else:
            llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        self.chain = prompt | llm

    def __call__(self, inputs):
        return self.chain.invoke(inputs)
