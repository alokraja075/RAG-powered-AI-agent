from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.core.config import get_settings


settings = get_settings()
_embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key, model=settings.embedding_model)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name='documents',
        embedding_function=_embeddings,
        persist_directory=settings.chroma_persist_directory,
    )


def chunk_text(text: str, source: str, user_id: int, document_id: int) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    return [
        Document(page_content=chunk, metadata={'source': source, 'user_id': str(user_id), 'document_id': str(document_id)})
        for chunk in chunks
        if chunk.strip()
    ]


def index_document(text: str, source: str, user_id: int, document_id: int) -> None:
    vector_store = get_vector_store()
    docs = chunk_text(text, source, user_id, document_id)
    if docs:
        vector_store.add_documents(docs)


def build_context(query: str, user_id: int, top_k: int):
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query, k=top_k, filter={'user_id': str(user_id)})
    context = '\n\n'.join([d.page_content for d in docs])
    sources = sorted({d.metadata.get('source', 'unknown') for d in docs})
    return context, sources


async def stream_answer(query: str, user_id: int, memory: list[dict], top_k: int):
    context, sources = build_context(query, user_id, top_k)
    system_prompt = (
        'You are a helpful RAG assistant. Use the provided context if relevant. '
        'If context is insufficient, say so clearly and answer from general knowledge. '
        'Always keep the answer concise and factual.'
    )
    message_list = [SystemMessage(content=system_prompt)]
    if context:
        message_list.append(SystemMessage(content=f'Context:\n{context}'))
    for msg in memory:
        if msg['role'] == 'assistant':
            message_list.append(AIMessage(content=msg['content']))
        else:
            message_list.append(HumanMessage(content=msg['content']))
    message_list.append(HumanMessage(content=query))

    llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0.2, streaming=True)
    full_text = ''
    async for chunk in llm.astream(message_list):
        piece = chunk.content or ''
        if piece:
            full_text += piece
            yield {'type': 'chunk', 'content': piece}

    yield {'type': 'sources', 'sources': sources}
    yield {'type': 'done', 'content': full_text}
