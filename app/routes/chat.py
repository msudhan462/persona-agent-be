from fastapi import APIRouter, Depends
from app.models.chat import *
from app.services.chat import chat
from app.auth_top_routers import get_current_user


# Router for item-related endpoints
router = APIRouter(prefix="/api/v1/chat")

# POST request to create an item
@router.post("/stream", status_code=200, summary="chat response streaming")
async def chat_stream(body: Convsersation, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.stream(body, current_user)


@router.post("/report", status_code=200, summary="reporting message")
async def chat_report(body: Report, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.report(body, current_user)


@router.post("/reaction", status_code=200, summary="reacting to message")
async def save_chat_reaction(body: PostReaction, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.save_reaction(body, current_user)


@router.get("/reaction", status_code=200, summary="get reaction message")
async def get_chat_reaction(body: GetReaction, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.get_reaction(body, current_user)


@router.post("/like", status_code=200, summary="store likes")
async def save_chat_likes(body: PostLike, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.save_likes(body, current_user)

@router.post("/dislike", status_code=200, summary="store dislikes")
async def save_chat_dislikes(body: PostDislike, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.save_dislikes(body, current_user)


@router.post("/get-likes-and-dislikes", status_code=200, summary="store likes and dislikes")
async def get_chat_likes_dislikes(body: GetLikesAndDislike, current_user=Depends(get_current_user)):
    print(body, current_user)
    return chat.get_likes_and_dislikes(body, current_user)

@router.post("/list-interactions", status_code=200, summary="get you interacted with others agents")
async def get_interactions(current_user=Depends(get_current_user)):
    print(current_user)
    return chat.list_interactions(current_user)

@router.post("/list-agents", status_code=200, summary="get others interacted with your agents")
async def get_agents(current_user=Depends(get_current_user)):
    print(current_user)
    return chat.list_agents(current_user)