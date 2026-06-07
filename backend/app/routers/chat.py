import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.entities import ChatMessage, User
from app.routers.deps import get_current_user
from app.schemas.chat import ChatRequest, ChatHistoryItem
from app.services.rag_service import stream_answer


router = APIRouter(prefix='/api/chat', tags=['chat'])


@router.get('/history', response_model=list[ChatHistoryItem])
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(100)
        .all()
    )
    return [
        ChatHistoryItem(role=m.role, content=m.content, created_at=m.created_at.replace(tzinfo=timezone.utc).isoformat())
        for m in messages
    ]


@router.post('/stream')
async def chat_stream(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    memory = [{'role': row.role, 'content': row.content} for row in reversed(history_rows)]

    db.add(ChatMessage(user_id=current_user.id, role='user', content=payload.query))
    db.commit()

    async def event_generator():
        answer = ''
        async for event in stream_answer(payload.query, current_user.id, memory=memory, top_k=payload.top_k):
            if event['type'] == 'chunk':
                answer += event['content']
            yield f"data: {json.dumps(event)}\n\n"
        db.add(ChatMessage(user_id=current_user.id, role='assistant', content=answer))
        db.commit()
        yield f"data: {json.dumps({'type': 'timestamp', 'created_at': datetime.utcnow().isoformat()})}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')
