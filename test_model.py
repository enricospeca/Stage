from agno.agent import Agent
from agno.models.ollama import Ollama
import os

agent = Agent(
    model=Ollama(id="gpt-oss:20b"),
    markdown=True
)

# optional dependencies
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import docx
except Exception:
    docx = None

def read_document(path: str) -> str:
    # always return a string or raise a clear error
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        if PdfReader is None:
            raise RuntimeError("PyPDF2 not installed. Run: pip install PyPDF2")
        text = []
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for p in reader.pages:
                text.append(p.extract_text() or "")
        return "\n".join(text)
    if ext in (".docx",):
        if docx is None:
            raise RuntimeError("python-docx not installed. Run: pip install python-docx")
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError(f"Unsupported file format: {ext}")

def chunk_text(text: str, max_chars: int = 3000):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = start + max_chars
        if end >= n:
            chunks.append(text[start:])
            break
        split_at = text.rfind(" ", start, end)
        if split_at <= start:
            split_at = end
        chunks.append(text[start:split_at])
        start = split_at + 1
    return chunks

def ask_question_about_file(agent: Agent, path: str, question: str):
    text = read_document(path)
    if not text or not text.strip():
        raise ValueError("No text extracted from the document.")
    chunks = chunk_text(text, max_chars=3000)

    # use user's question if provided, else default English fallback
    question = question.strip() or "Answer the following question based only on the document content."

    if len(chunks) == 1:
        prompt = (
            "Read the following document and answer the question based only on its content. "
            "Do not store or retain the document.\n\nDOCUMENT:\n"
            f"{text}\n\nQUESTION:\n{question}"
        )
        agent.print_response(prompt)
        return

    # for large documents include numbered chunks in the prompt (in English)
    prompt_parts = [
        "You have the following document divided into chunks. Answer the question using only the provided content. "
        "If the information is not present, say so explicitly."
    ]
    for i, c in enumerate(chunks, 1):
        prompt_parts.append(f"--- CHUNK {i}/{len(chunks)} ---\n{c}")
    prompt_parts.append(f"\nQUESTION:\n{question}")
    big_prompt = "\n\n".join(prompt_parts)
    agent.print_response(big_prompt)

if __name__ == "__main__":
    # Interactive usage
    path = input("File path (e.g. C:\\Stage\\Documenti\\esempio.pdf): ").strip()
    q = input("Question about the document (in English): ").strip()
    try:
        ask_question_about_file(agent, path, q)
    except Exception as e:
        print("Error:", e)