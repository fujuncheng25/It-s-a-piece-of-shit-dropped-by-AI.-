#!/usr/bin/env python3
import json
import math
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Tuple

PORT = 9130
OLLAMA_URL = "http://127.0.0.1:11434"
PREFERRED_MODELS = ["llama3.2", "llama3.1", "qwen2.5", "mistral"]
MAX_REQUEST_BYTES = 1_000_000

UVA_KNOWLEDGE = [
    {
        "title": "University of Virginia overview",
        "source": "https://www.virginia.edu/",
        "text": (
            "The University of Virginia (UVA) is a public research university in Charlottesville, Virginia. "
            "It was founded in 1819 by Thomas Jefferson."
        ),
    },
    {
        "title": "World Heritage connection",
        "source": "https://www.nps.gov/places/university-of-virginia.htm",
        "text": (
            "UVA's Academical Village, including the Rotunda and the Lawn, is part of the "
            "UNESCO World Heritage Site known as Monticello and the University of Virginia in Charlottesville."
        ),
    },
    {
        "title": "Governance and mission",
        "source": "https://www.virginia.edu/aboutuva",
        "text": (
            "UVA is a public institution governed by a Board of Visitors and emphasizes student self-governance, "
            "public service, and research."
        ),
    },
    {
        "title": "Schools and academics",
        "source": "https://www.virginia.edu/schools",
        "text": (
            "UVA includes schools and colleges spanning arts and sciences, engineering, business, law, medicine, "
            "education, nursing, and public policy."
        ),
    },
    {
        "title": "Athletics",
        "source": "https://virginiasports.com/",
        "text": (
            "UVA athletics teams are called the Cavaliers and compete in NCAA Division I, primarily in the Atlantic Coast Conference."
        ),
    },
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "where",
    "who",
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def _term_freq(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    counts: Dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    total = float(len(tokens))
    return {term: count / total for term, count in counts.items()}


def _cosine_sim(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(value * vec_b.get(term, 0.0) for term, value in vec_a.items())
    norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _rank_knowledge(question: str, top_k: int = 3) -> List[Dict[str, str]]:
    q_tokens = _tokenize(question)
    q_vec = _term_freq(q_tokens)
    q_set = set(q_tokens)
    scored: List[Tuple[float, Dict[str, str]]] = []
    for doc in UVA_KNOWLEDGE:
        d_tokens = _tokenize(doc["title"] + " " + doc["text"])
        d_vec = _term_freq(d_tokens)
        overlap = len(q_set.intersection(set(d_tokens)))
        score = float(overlap) + (_cosine_sim(q_vec, d_vec) / 100.0)
        scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def _http_json(url: str, payload: Dict) -> Dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _choose_model() -> str:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        available = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
        if not available:
            return PREFERRED_MODELS[0]
        for preferred in PREFERRED_MODELS:
            for model in available:
                if model == preferred or model.startswith(preferred + ":"):
                    return model
        return available[0]
    except Exception:
        return PREFERRED_MODELS[0]


def _build_prompt(question: str, context_docs: List[Dict[str, str]]) -> str:
    context = "\n\n".join(
        f"[{idx+1}] {doc['title']}\nSource: {doc['source']}\n{doc['text']}"
        for idx, doc in enumerate(context_docs)
    )
    return (
        "You are a factual UVA information assistant. Use only the provided context. "
        "If context is insufficient, say so briefly.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer concisely and include source numbers you used (like [1], [2])."
    )


def _generate_with_ollama(question: str, context_docs: List[Dict[str, str]]) -> Tuple[str, str]:
    prompt = _build_prompt(question, context_docs)
    model = _choose_model()
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = _http_json(f"{OLLAMA_URL}/api/generate", payload)
        answer = (response.get("response") or "").strip()
        if answer:
            return answer, model
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        pass

    fallback = " ".join(f"[{i+1}] {doc['text']}" for i, doc in enumerate(context_docs))
    return f"Ollama unavailable. Retrieved UVA context: {fallback}", model


def answer_question(question: str) -> Dict:
    question = (question or "").strip()
    if not question:
        return {"error": "Question cannot be empty."}

    context_docs = _rank_knowledge(question)
    answer, model = _generate_with_ollama(question, context_docs)
    return {
        "question": question,
        "answer": answer,
        "model": model,
        "sources": [{"title": d["title"], "source": d["source"]} for d in context_docs],
    }


class RAGRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: Dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json({"status": "ok", "service": "uva-rag", "port": PORT})
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/ask":
            self._send_json({"error": "Not found"}, status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_REQUEST_BYTES:
            self._send_json({"error": "Payload too large."}, status=413)
            return
        raw = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body."}, status=400)
            return

        result = answer_question(str(payload.get("question", "")))
        if "error" in result:
            self._send_json(result, status=400)
            return
        self._send_json(result)

    def log_message(self, msg_format: str, *args) -> None:
        return


def run_server() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), RAGRequestHandler)
    print(f"UVA RAG server running on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
