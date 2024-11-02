from fastapi import APIRouter, Depends, UploadFile
from app.models.home import *
from app.services.home import *
from app.auth_top_routers import get_current_user


# Router for item-related endpoints
router = APIRouter(prefix="/api/v1/")


@router.get("/recommendation/to-connect", status_code=200, summary="get list of recommend to connect")
async def remmended_to_connect( current_user=Depends(get_current_user)):
    print(current_user)
    return get_remmended_to_connect(current_user)



@router.get("/recommendation/to-chat", status_code=200, summary="get list of recommend to chat")
async def remmended_to_chat( current_user=Depends(get_current_user)):
    print(current_user)
    return get_remmended_to_chat(current_user)


@router.get("/search-agents", status_code=200, summary="search agents to chat")
async def searching_agents(body: SearchAgents, current_user=Depends(get_current_user)):
    print(body, current_user)
    return search_agents(body, current_user)
