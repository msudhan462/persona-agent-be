from app.routes.chat import router as chat_router
from app.auth.auth_routes import router as auth_router
from app.routes.agent import router as agent_router
from app.routes.data import router as data_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="My FastAPI Application",
    version="1.0.0",
    description="An API following FastAPI best practices."
)


origins = [
    "http://127.0.0.1:5000",  # your frontend URL
    "http://localhost:5000",   # optional, if you want to allow this too
    "http://35.169.165.29"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Replace "*" with a list of allowed origins, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Can also be ["GET", "POST", "OPTIONS"] if specific
    allow_headers=["*"],  # Can also specify allowed headers
)

# Include the routes
app.include_router(chat_router, tags=["Chat"])
app.include_router(agent_router, tags=["Agent"])
app.include_router(data_router, tags=["Data"])
app.include_router(auth_router, tags=["Authentication"])


@app.get("/", tags=["Root"], summary="Root Endpoint")
async def root():
    return {"message": "Welcome to the FastAPI app!"}
