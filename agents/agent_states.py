from typing import List

from pydantic import BaseModel, Field


class GradeLLMResponse(BaseModel):
    """Defines the structure for the agent's response output."""

    answer: str = Field(
        description="Extracts the most relevant answer found in the documents. If the initial document does not provide a valid answer (e.g., 'not found', 'None', or irrelevant), the response is taken from the next available document. If no relevant information is found in any document, return 'No Data Found'.",
    )
    raw_context: str = Field(
        description="Provides the raw context from the first relevant document. If the initial document's context is missing or not relevant, the next available document is used.",
    )
    found_doc_ids: List[int] = Field(
        description="A list of document IDs (doc_id values) retrieved from the source metadata. The output should be a list of integers.",
    )
    validation: str = Field(
        description="Determines if the answer is correct or not based on the raw context, returning either 'Correct' or 'Incorrect'."
    )
