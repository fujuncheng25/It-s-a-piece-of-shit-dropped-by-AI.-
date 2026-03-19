import unittest
from unittest.mock import patch

import rag_server


class RagServerTests(unittest.TestCase):
    @staticmethod
    def _call_do_get(path):
        captured = {}

        class DummyHandler:
            def _send_html(self, html, status=200):
                captured["html"] = html
                captured["status"] = status

            def _send_json(self, payload, status=200):
                captured["payload"] = payload
                captured["status"] = status

        DummyHandler.path = path
        rag_server.RAGRequestHandler.do_GET(DummyHandler())
        return captured

    def test_get_root_returns_web_ui(self):
        captured = self._call_do_get("/")
        self.assertEqual(captured["status"], 200)
        self.assertIn("<title>UVA RAG</title>", captured["html"])
        self.assertIn("<label for=\"question\">Question</label>", captured["html"])

    def test_get_health_returns_health_payload(self):
        captured = self._call_do_get("/health")
        self.assertEqual(captured["status"], 200)
        self.assertEqual(captured["payload"]["status"], "ok")

    def test_get_unknown_route_still_returns_not_found(self):
        captured = self._call_do_get("/missing")
        self.assertEqual(captured["status"], 404)
        self.assertEqual(captured["payload"]["error"], "Not found")

    def test_knowledge_is_hardcoded_from_uploaded_word_file(self):
        self.assertGreater(len(rag_server.UVA_KNOWLEDGE), 200)
        self.assertTrue(
            any(
                doc["source"] == "College_Search_Guide(1).docx"
                for doc in rag_server.UVA_KNOWLEDGE
            )
        )
        self.assertTrue(
            any(
                "College/University Search Guide" in doc["text"]
                for doc in rag_server.UVA_KNOWLEDGE
            )
        )

    def test_rank_knowledge_returns_relevant_docs(self):
        docs = rag_server._rank_knowledge("Who founded the University of Virginia?")
        self.assertTrue(docs)
        self.assertIn("founded", docs[0]["text"].lower())

    @patch("rag_server._generate_with_ollama")
    def test_answer_question_returns_sources_and_model(self, mocked_generate):
        mocked_generate.return_value = ("Thomas Jefferson founded UVA.", "llama3.2")
        result = rag_server.answer_question("Who founded UVA?")

        self.assertEqual(result["model"], "llama3.2")
        self.assertIn("sources", result)
        self.assertGreater(len(result["sources"]), 0)
        self.assertIn("Thomas Jefferson", result["answer"])

    def test_answer_question_rejects_empty(self):
        result = rag_server.answer_question("   ")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
