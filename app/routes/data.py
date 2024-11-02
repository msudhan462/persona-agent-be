from fastapi import APIRouter, Depends, UploadFile
from app.models.data import *
from app.services.data import data
from app.auth_top_routers import get_current_user


# Router for item-related endpoints
router = APIRouter(prefix="/api/v1/data")

# POST request to create an item
@router.post("/ingest/file", status_code=200, summary="ingest file")
async def ingest_file(file: UploadFile, current_user=Depends(get_current_user)):
    print(file, current_user)
    return data.upload_file(file, current_user)

@router.post("/ingest/qa", status_code=200, summary="ingest Q & A")
async def ingest_qa(body:IngestQA, current_user=Depends(get_current_user)):
    print(body, current_user)
    return data.qa(body, current_user)

@router.post("/ingest/text", status_code=200, summary="ingest plain text")
async def ingest_qa(body:IngestText, current_user=Depends(get_current_user)):
    print(body, current_user)
    return data.text(body, current_user)


@router.get("/list-files", status_code=200, summary="list files")
async def list_files(current_user=Depends(get_current_user)):
    print(current_user)
    return data.list_files(current_user)

@router.delete("/delete-file", status_code=200, summary="delete files")
async def delete_file(body:DeleteFile, current_user=Depends(get_current_user)):
    print(body, current_user)
    return data.delete_file(body, current_user)

@router.get("/get-qa", status_code=200, summary="get Q&A")
async def get_qa(body:GetQA, current_user=Depends(get_current_user)):
    print(current_user)
    return data.get_qa(body, current_user)

@router.get("/get-text", status_code=200, summary="get text")
async def get_text(current_user=Depends(get_current_user)):
    print(current_user)
    return data.get_text(current_user)