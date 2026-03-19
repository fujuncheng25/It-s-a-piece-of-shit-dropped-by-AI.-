import unittest
from unittest.mock import patch

import rag_server


class RagServerTests(unittest.TestCase):
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
