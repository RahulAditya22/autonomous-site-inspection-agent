from app.rag.store import RAGStore
from pathlib import Path
def test_rag_knowledge_base_has_safety_sections():
    hits=RAGStore(Path('data/knowledge')).retrieve('fire smoke incident critical'); assert any('fire' in h['text'].lower() for h in hits)
