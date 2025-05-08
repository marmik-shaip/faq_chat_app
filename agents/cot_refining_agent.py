import json

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


def get_model(model, temperature=0.0):
    if "gpt" in model:
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
    else:
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )


class ExtractionResponse(BaseModel):
    """
    A model representing the extraction outcome from processed documents.

    Attributes:
        scratch_pad (list[str]): A list of notes or intermediate steps outlining the thought process used during extraction.
        response (str): The final extracted output or summarized result from the document processing.
    """

    scratch_pad: list[str] = Field(
        description="A list of intermediate steps or notes detailing the thought process during extraction."
    )
    response: str = Field(
        description="The final output or result obtained after processing the document."
    )


class GradingResponse(BaseModel):
    """
    Represents the outcome of an evaluation by an LLM acting as a judge.

    This model is typically used in systems where a language model is tasked with
    assessing the quality, correctness, or compliance of another generated response
    based on predefined rules or guidelines.
    """

    verdict: str = Field(
        description="The final judgment of the evaluation — either 'pass' or 'fail'. "
        "Use 'pass' if the response meets the expected criteria or follows the correct rule; "
        "'fail' if it does not."
    )

    reasons: str = Field(
        description="A detailed explanation supporting the verdict. "
        "Describe whether the appropriate rule was followed, the response structure and content were accurate, "
        "and if all critical requirements were satisfied. "
        "Also highlight any inclusion of disallowed elements or significant omissions."
    )

    feedback: str = Field(
        description="Constructive suggestions for improving the evaluated response. "
        "This may include tips on better formatting, completeness, accuracy, clarity, or adherence to rules."
    )


class DocumentInformation(BaseModel):
    """
    A model representing key extracted information from a medical document.

    Attributes:
        scratch_pad (list[str]): A list of notes or intermediate steps outlining the thought process used during extraction.

        date_of_service (str): The date when the service was provided,
            expected in the format MM/DD/YYYY (e.g., "04/10/2025").

        patient_name (str): The full name of the patient, formatted as
            "FirstName LastName" (e.g., "John Doe"). Middle names or titles should be excluded.

        physician_name (str): The full name of the primary physician associated with
            the Date of Service, formatted as "Full Name, MD" (e.g., "Alice Price, MD").
    """

    scratchpad: str = Field(
        description="A list of intermediate steps or notes detailing the thought process during extraction."
    )

    date_of_service: str = Field(
        description="Date of Service in the format MM/DD/YYYY (e.g., '04/10/2025')"
    )
    patient_name: str = Field(
        description='Full patient name in "FirstName LastName" format (e.g., "John Doe")'
    )
    physician_name: str = Field(
        description='Primary physician name in "Full Name, MD" format (e.g., "Alice Price, MD")'
    )


class StructuredExtractor:
    def __init__(
        self,
        extractor_prompt,
        grading_prompt,
        extraction_model,
        grading_model,
        grading_steps=0,
    ):
        self.extraction_chain = extractor_prompt | get_model(
            model=extraction_model
        ).with_structured_output(DocumentInformation)
        self.grader_chain = grading_prompt | get_model(model=grading_model)
        self.grading_steps = 0

    def __call__(self, docs: list[HumanMessage]):
        inputs = {"documents": [HumanMessage(content="## **Documents**")] + docs}
        extraction = self.extraction_chain.invoke(inputs)
        extractions = [{"extraction": extraction.model_dump()}]
        grade_text = AIMessage(content="")

        for grade_turn in range(self.grading_steps):
            print(f"Grade Turn: {grade_turn+1}")
            qa_inputs = {
                "documents": [HumanMessage(content="## **Documents**")] + docs,
                "output": [
                    HumanMessage(
                        content=f"## **Output**\n{json.dumps(extraction.model_dump(), indent=2)}"
                    ),
                ],
            }
            grade_text = self.grader_chain.invoke(qa_inputs)
            refine_inputs = {
                "documents": [HumanMessage(content="## **Documents**")] + docs,
                "previous_output": [
                    HumanMessage(
                        content=f"## **Output**\n{json.dumps(extraction.model_dump(), indent=2)}"
                    ),
                ],
                "feedback": [HumanMessage(content=grade_text.content)],
            }
            extraction = self.extraction_chain.invoke(refine_inputs)
            extractions.append(
                [{"extraction": extraction.model_dump(), "grade": grade_text.content}]
            )

        return (
            GradingResponse(verdict="", reasons=grade_text.content, feedback=""),
            extraction,
            extractions,
        )


class CotRefiningAgent:
    def __init__(
        self,
        extraction_prompt,
        grader_prompt,
        extraction_model="gpt-4o-mini",
        grader_model="gpt-4o-mini",
        grading_steps=0,
    ):
        self.extraction_chain = extraction_prompt | get_model(
            extraction_model, 0.0
        ).with_structured_output(ExtractionResponse)
        self.grader_chain = grader_prompt | get_model(grader_model, 0.0)
        self.grader_response_chain = PromptTemplate.from_template(
            "Convert this given response into structured output\n\n**Response**\n{response}\n\n"
        ) | get_model("gpt-4o-mini", temperature=0.0).with_structured_output(
            GradingResponse
        )
        self.grading_steps = 0
        print(f"Number of grading steps {self.grading_steps}")

    def __call__(self, docs: list[HumanMessage]):
        inputs = {"documents": [HumanMessage(content="## **Documents**")] + docs}
        extraction = self.extraction_chain.invoke(inputs)
        extractions = [{"extraction": extraction.model_dump()}]
        grade_text = AIMessage(content="")

        for grade_turn in range(self.grading_steps):
            print(f"Grade Turn: {grade_turn+1}")
            steps = "\n".join(extraction.scratch_pad)
            qa_inputs = {
                "documents": [HumanMessage(content="## **Documents**")] + docs,
                "output": [
                    HumanMessage(
                        content=f"## Steps Taken:\n{steps}\n\n## **Output**\n{extraction.response}"
                    ),
                ],
            }
            grade_text = self.grader_chain.invoke(qa_inputs)

            # if grade.verdict == 'pass':
            #     return grade, extraction

            refine_inputs = {
                "documents": [HumanMessage(content="## **Documents**")] + docs,
                "previous_output": [
                    HumanMessage(
                        content=f"## Steps Taken:\n{steps}\n\n## **Output**\n{extraction.response}"
                    ),
                ],
                "feedback": [HumanMessage(content=grade_text.content)],
            }
            extraction = self.extraction_chain.invoke(refine_inputs)
            extractions.append(
                {"extraction": extraction.model_dump(), "grade": grade_text.content}
            )
        # grade = self.grader_response_chain.invoke({'response': grade_text.content})
        return (
            GradingResponse(verdict="", reasons=grade_text.content, feedback=""),
            extraction,
            extractions,
        )
