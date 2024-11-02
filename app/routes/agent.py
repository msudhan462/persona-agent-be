from fastapi import APIRouter, Depends
from app.models.agent import *
from app.services.agent import agent
from app.auth_top_routers import get_current_user


# Router for item-related endpoints
router = APIRouter(prefix="/api/v1/agent")

@router.post('/connect', status_code=200, summary="connect to agent")
def agent_connect(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.connect(body, current_user)

@router.post('/disconnect', status_code=200, summary="disconnect to agent")
def agent_disconnect(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.disconnect(body, current_user)

@router.post('/connect/status', status_code=200, summary="get connection status")
def agent_connect_status(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.connect_status(body, current_user)


@router.post('/report', status_code=200, summary="report the agent")
def agent_report(body: AgentReport, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.report(body, current_user)


@router.post('/block', status_code=200, summary="block the agent")
def agent_block(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.block(body, current_user)



@router.post('/unblock', status_code=200, summary="unblock the agent")
def agent_unblock(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.unblock(body, current_user)



@router.get('/block/status', status_code=200, summary="get block status")
def agent_block_status(body: PesonaID, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.block_status(body, current_user)



@router.get('/current-status', status_code=200, summary="get current feeling")
def agent_block_status(body: CurrentStatus, current_user=Depends(get_current_user)):
    print(body, current_user)
    return agent.current_status(body, current_user)


