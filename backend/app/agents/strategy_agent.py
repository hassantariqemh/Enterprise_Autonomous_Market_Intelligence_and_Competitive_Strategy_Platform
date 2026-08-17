import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

SYSTEM_PROMPT = """You are a market intelligence strategy advisor for a consumer
electronics company. You are given structured competitor data extracted from a
knowledge graph. Answer the executive's question using only this data.

Rules:
- Base your answer strictly on the data provided.
- Cite specific numbers or facts from the data as evidence.
- Give a confidence score (0-100) based on how directly the data supports the answer.
- If the data is insufficient, say so clearly.
- Keep the answer concise, 3-5 sentences.
"""


def run(question: str, evidence: dict) -> dict:
    """
    Strategy Advisor Agent.
    Reasons over evidence from other agents and produces an explainable answer.
    """
    user_prompt = f"Question: {question}\n\nEvidence from Knowledge Graph:\n{evidence}"

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    return {
        "question": question,
        "answer": response.content,
        "evidence_used": evidence,
    }