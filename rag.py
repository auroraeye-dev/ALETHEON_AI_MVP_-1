import os
from dotenv import load_dotenv
import faiss
import numpy as np
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SimpleRAG:

    def __init__(self):
        self.text_chunks = []
        self.index = None

    def embed(self, texts):
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return np.array([d.embedding for d in resp.data]).astype("float32")

    def build(self, documents, chunk_size=500):

        for doc in documents:
            if not doc:
                continue

            for i in range(0, len(doc), chunk_size):
                self.text_chunks.append(doc[i:i+chunk_size])

        if not self.text_chunks:
            return

        embeddings = self.embed(self.text_chunks)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def query(self, question, k=10):

        if self.index is None:
            return []

        q_embed = self.embed([question])
        _, indices = self.index.search(q_embed, k)

        return [self.text_chunks[i] for i in indices[0]]

    def ask(self, question):

        chunks = self.query(question)

        print("\n========== RETRIEVED CHUNKS ==========\n")

        for i, c in enumerate(chunks):
            print(f"\n--- Chunk {i+1} ---\n")
            print(c[:1000])

        context = "\n".join(chunks)

        prompt = f"""
Only use this context.

If answer not found say NO DATA FOUND.

Context:
{context}

Question:
{question}
"""

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return r.choices[0].message.content