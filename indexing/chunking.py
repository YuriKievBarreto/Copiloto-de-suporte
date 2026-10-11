from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
import re
from langchain_core.documents import Document
from pathlib import Path


MAX_CHARS = 1200 
CHAVES = {
    "categoria": "categoria",
    "tipo": "tipo",
    "versão": "versao",
    "última atualização": "atualizado_em",
}
META_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$", re.MULTILINE)

split_h2 = MarkdownHeaderTextSplitter([("##", "secao")])
split_h3 = MarkdownHeaderTextSplitter([("##", "secao"), ("###", "subsecao")])

fallback = RecursiveCharacterTextSplitter(
    chunk_size=MAX_CHARS, chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " "],
)


def chunk_document(path: Path):
    raw = path.read_text(encoding="utf-8")

    topo, _, corpo = raw.partition("\n---\n")
    titulo = re.match(r"#\s+(.+)", topo).group(1).strip()

    meta = {
        CHAVES[k.strip().lower()]: v.strip()
        for k, v in META_RE.findall(topo)
        if k.strip().lower() in CHAVES
    }
    meta.update(titulo=titulo, fonte=path.name)

    corpo = re.sub(r"^---\s*$", "", corpo, flags=re.MULTILINE)

    chunks: list[Document] = []
    for sec in split_h2.split_text(corpo):
        if len(sec.page_content) <= MAX_CHARS:
            chunks.append(sec)
            continue
        for sub in split_h3.split_text(sec.page_content):
            if len(sub.page_content) <= MAX_CHARS:
                chunks.append(sub)
            else:
                chunks.extend(fallback.split_documents([sub]))


    for c in chunks:
        caminho = " > ".join(
            x for x in (titulo, c.metadata.get("secao"), c.metadata.get("subsecao")) if x
        )
        c.page_content = f"[{caminho}]\n{c.page_content.strip()}"
        c.metadata.update(meta)
    return chunks



def chunk_all_documents(path: str):
    todos = []
    for p in sorted(Path(path).rglob("*.md")):
        todos.extend(chunk_document(p))

    return todos


