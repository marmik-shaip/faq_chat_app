import json
import logging
from typing import List, Optional, Dict, Any

import chromadb
from chromadb import Settings
from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

import container
from entities.server_entities import ChatHistory
from repositories.chroma_db_repo import DocRepository

load_dotenv(".env")

openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=3072)


class AdvancedDocumentQAAgent:
    @inject
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        db: DocRepository = Provide[container.Container.doc_repo],
        verbose: bool = True,
    ):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.system_prompt = db.get_prompt_by_prompt_name("Chatbot System Prompt")
        self.verbose = verbose

    def get_chroma_client(self, collection_name: str):
        try:
            http_client = chromadb.PersistentClient("./chroma_db")
            # .HttpClient(
            #     host="10.142.152.101",
            #     port=8000,
            #     ssl=False,
            #     settings=Settings(anonymized_telemetry=False),
            # ))

            chroma_client = Chroma(
                client=http_client,
                collection_name=collection_name,
                embedding_function=openai_embeddings,
            )

            return chroma_client

        except Exception as e:
            self.log.error(f"Chroma client creation failed: {str(e)}")
            raise

    def retrieve_documents(
        self, query: str, collection_name: str, document_ids: Optional[List] = None
    ):
        try:
            chroma_client = self.get_chroma_client(collection_name)

            retriever = chroma_client.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.90},
            )

            if document_ids:
                retriever.search_kwargs["filter"] = {"doc_id": {"$in": document_ids}}

            results = retriever.invoke(query)
            print("Results by retriever: ", results)
            formatted_results = []
            doc_ids = []

            for result in results:
                doc_id = result.metadata.get("doc_id")
                if doc_id and doc_id not in doc_ids:
                    doc_ids.append(doc_id)

                formatted_results.append(
                    {"content": result.page_content, "metadata": result.metadata}
                )

            return formatted_results, doc_ids

        except Exception as e:
            self.log.error(f"Document retrieval failed: {str(e)}")
            return [], []

    def format_context(self, results):
        context_chunks = []

        for idx, result in enumerate(results, 1):
            doc_id = result["metadata"].get("doc_id", "Unknown")
            source = result["metadata"].get("source", "Unknown source")
            content = result["content"]

            context_chunks.append(
                f"[Document {idx} - ID: {doc_id}]\nSource: {source}\nContent: {content}\n"
            )

        return "\n".join(context_chunks)

    def process_chat_history(
        self, chat_history: Optional[List[ChatHistory]] = None
    ) -> List[BaseMessage]:
        if not chat_history:
            return []
        print("Chat history: ", chat_history)
        converted_history = []
        for message in chat_history:
            role = message.question
            ans = message.answer
            if role:
                converted_history.append(HumanMessage(content=role))
            if ans:
                converted_history.append(AIMessage(content=ans))
        print("Converted History: ", converted_history)
        return converted_history

    def format_chat_history(self, processed_history: List[BaseMessage]) -> str:
        if not processed_history:
            return "No previous chat history."

        history_texts = []
        for msg in processed_history:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            history_texts.append(f"{role}: {msg.content}")

        return "\n".join(history_texts)

    def generate_answer(
        self, query: str, context: str, chat_history: List[BaseMessage]
    ) -> str:
        print("System prompt: ", self.system_prompt)
        system_prompt = SystemMessage(content=self.system_prompt)
        chat_lst = [system_prompt]
        if chat_history:
            chat_lst.extend(chat_history[:20])

        final_content = f"Context: {context}\n\nQuery: {query}\n\nAnswer the query based on the context provided."
        chat_lst.append(HumanMessage(content=final_content))

        chat_prompt = ChatPromptTemplate.from_messages(chat_lst)
        formatted_prompt = chat_prompt.format_messages(data="")

        try:
            print("Formatted Prompt: ", formatted_prompt)
            return self.llm.invoke(formatted_prompt)

        except Exception as e:
            self.log.error("Error running agent", exc_info=True)
            raise

    def run_query(
        self,
        query: str,
        collection_name: str,
        document_ids: Optional[List[int]] = None,
        chat_history: Optional[List[ChatHistory]] = None,
        custom_system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:

        self.log.info(f"Running query: {query} on collection: {collection_name}")

        processed_history = self.process_chat_history(chat_history)
        print("Processed History: ", processed_history)

        self.log.info(f"Retrieving documents from collection: {collection_name}")

        results, found_doc_ids = self.retrieve_documents(
            query, collection_name, document_ids
        )
        print("Results: ",results)
        context = self.format_context(results)
        # print("Context: ",context)

        intermediate_steps = []

        if results:
            intermediate_steps.append(("document_search", json.dumps(results)))
            # print("Intermediate Steps: ", intermediate_steps)
        if context:
            self.log.info("Generating answer using RAG")
            answer = self.generate_answer(query, context, processed_history)
        else:
            self.log.warning("No relevant documents found")
            answer = "No Data Found"

        return {"output": answer, "found_doc_ids": found_doc_ids}

    def run_query_on_entire_document(
        self,
        query: str,
        metadata: Dict[str, str],
        doc_content: str,
        chat_history: Optional[List[ChatHistory]] = None,
        custom_system_prompt: Optional[str] = None,
    ):
        self.system_whole_doc_prompt = """## Objective
You are an expert document search and Q&A assistant. Your goal is to accurately answer the user’s query by retrieving and presenting relevant information solely from the provided document context.

## Input
- **User Query:** The specific question or inquiry posed by the user.
- **Context:** Passages retrieved from various documents based on the user's query.
- **Chat History:** Previous interactions that may be relevant to the current query.

## Instructions

1. **Comprehend the Query:**  
   Understand what the user is asking and identify the key aspects of their inquiry.

2. **Synthesize a Single Comprehensive Answer:**  
   Based on all the provided document contexts, craft one complete response that thoroughly addresses the user's query. Consolidate all relevant details, data points, and insights into a single, cohesive answer. The final output must be a single JSON object (one dictionary) that integrates all necessary information, without splitting the answer into multiple parts.

3. **No Additional Content:**  
   Do not include any extra commentary, notes, or explanations beyond the required answer output.

4. **Extract Crucial Details:**  
   Identify and extract all crucial details, data points, and nuanced insights that capture the document's main intent.

5. **Identify Explicit and Implicit Information:**  
   Capture both direct answers and any implied information from the context that may respond to the user query.

6. **Versatile Document Types:**  
   Be prepared to work with various document types (e.g., FAQ, reports, narratives, descriptions) and develop a clear understanding of the user's question using the provided context.

7. **Handling No Match:**  
   If, after thoroughly analyzing the context, no relevant answer can be found, return exactly:
   ```
   "No Data Found"
   ```

8. **Output Metadata:**  
   Every output dictionary must include a `source_metadata` field formatted exactly as follows:
   ```json
   "source_metadata": {{ "doc_id": <number>, "source": "<filepath_or_document_source>" }}
   ```
   - Use this format for every instance where relevant information is found.

## Output Format

The final output should be a **single JSON object** (one dictionary) that includes the following keys:

- **"source_metadata"**: A JSON array of objects, each containing the document's metadata in the precise format given above.
- **"raw_context"**: An exact snippet or passage from the document that contains the relevant information.
- **"summary"**: A concise summary that directly references the extracted snippet.
- **"answer"**: A detailed explanation that integrates all the necessary information from the context into one complete response.

### Expected Output Example

```json
{{
    "source_metadata": [
        {{ "doc_id": 1234, "source": "downloaded_docs/abcd.pdf" }},
        {{ "doc_id": 5678, "source": "downloaded_docs/efgh.pdf" }}
    ],
    "raw_context": "Exact snippets from the document(s) with the relevant information.",
    "summary": "A concise summary referencing the extracted snippet(s).",
    "answer": "A detailed, comprehensive answer that integrates all the relevant information and insights into a single, unified response."
}}
```

If no relevant information is found, the output must be exactly:

```
"No Data Found"
```"""
        processed_history = (
            self.process_chat_history(chat_history) if chat_history else []
        )

        history_text = (
            "\n".join(
                f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                for msg in processed_history
            )
            if processed_history
            else ""
        )
        # print("History Text: ", history_text)
        # print("Processed History: ", processed_history)
        system_prompt = (
            custom_system_prompt
            if custom_system_prompt
            else self.system_whole_doc_prompt
        )
        prompt_template = PromptTemplate(
            input_variables=["chat_history", "doc_content", "query", "metadata"],
            template=(
                f"{system_prompt}\n\n"
                "User Query:\n{query}\n\n"
                "Metadata:\n{metadata}\n\n"
                "Document Content:\n{doc_content}\n\n"
                "Chat History:\n{chat_history}\n\n"
                "Please answer based solely on the above document."
            ),
        )

        try:
            formatted_prompt = prompt_template.format(
                query=query,
                metadata=json.dumps(metadata),
                doc_content=doc_content,
                chat_history=history_text,
            )
            print(formatted_prompt)
            return self.llm.invoke(formatted_prompt)

        except Exception as e:
            self.log.error("Error processing document", exc_info=True)
            raise
