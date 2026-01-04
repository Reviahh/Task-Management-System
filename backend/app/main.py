"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routes.tasks import router as tasks_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    print("[OK] Database initialized")
    yield
    # Shutdown
    print("[BYE] Application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="""
    ## Intelligent Task Management System
    
    A smart task management API with AI-powered features:
    
    ### Core Features
    - **CRUD Operations**: Create, Read, Update, Delete tasks
    - **Filtering & Sorting**: Filter by status, priority, tags; sort by various fields
    - **Pagination**: Efficient data retrieval with pagination
    
    ### AI Features
    - **Natural Language Parsing**: Create tasks from natural language input
    - **Smart Tag Suggestions**: AI-powered tag recommendations
    - **Priority Suggestions**: Intelligent priority recommendations
    - **Task Breakdown**: Split complex tasks into subtasks
    - **Semantic Search**: Find tasks by meaning, not just keywords
    - **Task Summaries**: AI-generated task insights and summaries
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Intelligent Task Management System",
        "docs": "/docs",
        "api_prefix": "/api"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "ai_available": bool(settings.openai_api_key)}

