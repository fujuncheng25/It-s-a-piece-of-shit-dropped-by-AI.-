import unittest
from unittest.mock import patch

import rag_server


class RagServerTests(unittest.TestCase):
    def test_get_root_returns_health_payload(self):
        captured = {}

        class DummyHandler:
            path = "/"

            def _send_json(self, payload, status=200):
                captured["payload"] = payload
                captured["status"] = status

        rag_server.RAGRequestHandler.do_GET(DummyHandler())
        self.assertEqual(captured["status"], 200)
        self.assertEqual(captured["payload"]["status"], "ok")

    def test_get_unknown_route_still_returns_not_found(self):
        captured = {}

        class DummyHandler:
            path = "/missing"

            def _send_json(self, payload, status=200):
                captured["payload"] = payload
                captured["status"] = status

        rag_server.RAGRequestHandler.do_GET(DummyHandler())
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
