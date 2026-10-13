from app.core.database.vector_database import get_vector_store
from tqdm import tqdm
import uuid
from collections import defaultdict
from indexing.chunking import chunk_all_documents
vector_store = get_vector_store()
DOCUMENTS_PATH = "rag_documents"

def make_ids(chunks) -> list[str]:
    """UUID determinístico por (arquivo, posição do chunk dentro do arquivo)."""
    posicao = defaultdict(int)
    ids = []
    for c in chunks:
        fonte = c.metadata["fonte"]
        ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fonte}#{posicao[fonte]}")))
        posicao[fonte] += 1
    return ids


def ingest():
    chunks = chunk_all_documents(DOCUMENTS_PATH)
    ids = make_ids(chunks)

    LOTE = 16
    for i in tqdm(range(0, len(chunks), LOTE), desc="Indexando"):
        vector_store.add_documents(chunks[i:i + LOTE], ids=ids[i:i + LOTE])




if __name__ == "__main__":
    ingest()