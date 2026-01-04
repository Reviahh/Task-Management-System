"""FastAPI application entry point."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from app.config import get_settings
from app.database import init_db, AsyncSessionLocal
from app.routes.tasks import router as tasks_router
from app.logging_config import logger

settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(start_time * 1000)}"
        
        # Log request
        logger.info(
            f"Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log response
        logger.info(
            f"Request completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Cache control for API responses
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Application starting up")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Application shutting down")


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
    - **Task Categorization**: Automatic task classification
    - **Similar Task Detection**: Find related tasks
    - **Task Insights**: Analytics and recommendations
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware for frontend
# In production, specify exact origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

# Include routers
app.include_router(tasks_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Intelligent Task Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns the health status of the application and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {
            "api": "ok",
            "database": "unknown",
            "ai_service": "unavailable"
        }
    }
    
    # Check database connectivity
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI service availability
    if settings.openai_api_key:
        health_status["checks"]["ai_service"] = "available"
    else:
        health_status["checks"]["ai_service"] = "fallback_mode"
    
    return health_status


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return Response(status_code=503, content='{"status": "not_ready"}')

