import json

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel, Field

from agents.prompts import UPDATER_PROMPT, GRADER_PROMPT, COMBINER_PROMPT
from common.llm_helper import StructuredLLM, SimpleLLM
from entities.grader_entities import GradingInformation


class SubjectiveOutput(BaseModel):
    output: str = Field(description="Markdown formatted subjective content")


class ReviewOfSystemsOutput(BaseModel):
    output: str = Field(description="Markdown formatted review of systems content")


class ExamOutput(BaseModel):
    output: str = Field(description="Markdown formatted exam content")


class AssessmentPlanOutput(BaseModel):
    output: str = Field(description="Markdown formatted Assessment & Plan content")


class CodeStatusOutput(BaseModel):
    output: str = Field(description="Markdown formatted code status content")


class FooterOutput(BaseModel):
    output: str = Field(description="Markdown formatted footer content")


class ProgressNoteOutput(BaseModel):
    output: str = Field(description="Markdown formatted combined progress note content")


class SubjectiveExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt, SubjectiveOutput, model=model, temperature=temperature
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class ROSExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt,
            ReviewOfSystemsOutput,
            model=model,
            temperature=temperature,
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class ExamExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt, ExamOutput, model=model, temperature=temperature
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class AssessmentPlanExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt, AssessmentPlanOutput, model=model, temperature=temperature
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class CodeStatusExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt, CodeStatusOutput, model=model, temperature=temperature
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class FooterExtractorAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        extractor_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=UPDATER_PROMPT),
                HumanMessage(content="**Progress Note Content**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                MessagesPlaceholder("qa", optional=True),
            ]
        )
        self.llm = StructuredLLM(
            extractor_prompt, FooterOutput, model=model, temperature=temperature
        )

    def __call__(
        self, progress_note, orders, lab_report, vital_signs, output=None, grade=None
    ):

        inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
        }
        if output is not None and grade is not None:
            print(
                f"Adding QA. Output is {output.output} \n\n --------------------- \n\n Grade is {grade.model_dump()}"
            )
            inputs["qa"] = [
                HumanMessage(
                    content=f" **Previously extracted content** \n{output.output} \n Strictly follow the following QA's instructions. \n{json.dumps(grade.model_dump())}"
                )
            ]
        output = self.llm(inputs)
        return output


class ExtractionCombiner:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=COMBINER_PROMPT),
                MessagesPlaceholder("documents"),
            ]
        )
        self.llm = StructuredLLM(
            prompt, ProgressNoteOutput, model=model, temperature=temperature
        )

    def __call__(self, outputs):
        inputs = [
            HumanMessage(
                content=f"```json\n{json.dumps(out.model_dump(), indent=2)}\n```"
            )
            for out in outputs
        ]
        return self.llm(inputs)


class PageGraderAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        grader_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(GRADER_PROMPT),
                HumanMessage(content="**Old Progress Note**"),
                MessagesPlaceholder("progress_note", optional=True),
                HumanMessage(content="**Orders Summary**"),
                MessagesPlaceholder("orders", optional=True),
                HumanMessage(content="**Lab Report**"),
                MessagesPlaceholder("lab_report", optional=True),
                HumanMessage(content="**Vital Signs**"),
                MessagesPlaceholder("vital_signs", optional=True),
                HumanMessage(content="**Updated Progress Note**"),
                MessagesPlaceholder("content", optional=True),
            ]
        )
        self.grader = SimpleLLM(grader_prompt, model=model, temperature=temperature)
        self.output_formatter = StructuredLLM(
            ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(
                        "Your job is to summarise the following text into Json. Should include all the points in the reasons and appropriate instructions to mitigate any errors. \n\n {response}"
                    ),
                ]
            ),
            GradingInformation,
            model="gpt-4o-mini",
        )

    def __call__(
        self,
        progress_note,
        orders,
        lab_report,
        vital_signs,
        outputs: ProgressNoteOutput,
    ) -> GradingInformation:
        llm_inputs = {
            "progress_note": [progress_note],
            "orders": [orders],
            "lab_report": [lab_report],
            "vital_signs": [vital_signs],
            "content": [
                HumanMessage(
                    content=f"```json\n{json.dumps(outputs.model_dump(), indent=2)}\n```"
                )
            ],
        }

        grade = self.grader(llm_inputs)
        content = grade.content
        llm_inputs = {"response": grade.content}
        grade = self.output_formatter(llm_inputs)
        return content, grade
