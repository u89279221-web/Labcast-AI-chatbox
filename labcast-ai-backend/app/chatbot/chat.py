import logging
from app.chatbot.retriever import retriever
from app.chatbot.llm import call_llm

logger = logging.getLogger(__name__)

def process_chat_query(machine_id: str, question: str) -> dict:
    """
    Processes a chat query for a specific machine.
    Uses RAG: retrieves relevant chunks and calls the LLM.
    """
    logger.info(f"Processing chat query for machine '{machine_id}': {question}")
    
    # 1. Retrieve top context snippets
    snippets = retriever.search(machine_id, question, top_k=3)
    
    if not snippets:
        return {
            "answer": "I don't have any manual or documentation for this machine to answer your question.",
            "source_snippet": ""
        }
        
    context_text = "\n\n".join([f"--- Snippet {i+1} ---\n{s}" for i, s in enumerate(snippets)])
    most_relevant_snippet = snippets[0]
    
    # 2. Build the prompt
    prompt = f"""You are an expert laboratory assistant. 
Please answer the user's question using ONLY the provided context snippets from the machine's manual.
If the answer is not contained in the context, explicitly say that you do not know.

Context:
{context_text}

Question:
{question}
"""

    # 3. Call the LLM
    answer = call_llm(prompt, fallback_snippet=most_relevant_snippet)
    
    return {
        "answer": answer,
        "source_snippet": most_relevant_snippet
    }
