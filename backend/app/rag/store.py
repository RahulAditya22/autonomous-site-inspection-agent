from __future__ import annotations
from pathlib import Path
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
class RAGStore:
    def __init__(self,knowledge_dir):
        self.dir=Path(knowledge_dir); self.dir.mkdir(parents=True,exist_ok=True); self.docs=[]; self.vectorizer=None; self.matrix=None; self._load()
    def _load(self):
        for path in sorted(self.dir.glob('*.md')):
            sections=re.split(r'\n(?=## )',path.read_text(encoding='utf-8'))
            for sec in sections:
                sec=sec.strip()
                if sec:
                    title=sec.splitlines()[0].lstrip('# ').strip(); body='\n'.join(sec.splitlines()[1:]).strip(); self.docs.append({'source':path.name,'section':title,'text':title+'\n'+body})
        corpus=[d['text'] for d in self.docs]
        if corpus:self.vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2)); self.matrix=self.vectorizer.fit_transform(corpus)
    def retrieve(self,query,top_k=3):
        if not self.docs or self.vectorizer is None:return []
        q=self.vectorizer.transform([query]); sims=(self.matrix@q.T).toarray().ravel(); idx=np.argsort(-sims)[:top_k]
        return [{**self.docs[i],'score':round(float(sims[i]),3)} for i in idx if sims[i]>0]
