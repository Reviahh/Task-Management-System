"""Task API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    NaturalLanguageTaskInput,
    ParsedTaskFromNL,
    TaskBreakdownResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
    TagSuggestionResponse,
    PrioritySuggestionResponse,
    TaskSummaryRequest,
    TaskSummaryResponse,
    SimilarTaskRequest,
    SimilarTaskResponse,
    SimilarTaskResult,
    TaskCategoryRequest,
    TaskCategoryResponse,
    TaskInsightsResponse,
)
from app.services.task_service import task_service
from app.services.ai_service import ai_service
import math

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task = await task_service.create_task(db, task_data)
    return task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """List all tasks with filtering, sorting, and pagination."""
    skip = (page - 1) * page_size
    tags_list = tags.split(",") if tags else None
    
    tasks, total = await task_service.get_tasks(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        priority=priority,
        tags=tags_list,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a task by ID."""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    task = await task_service.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


# AI-powered endpoints

@router.post("/ai/parse", response_model=ParsedTaskFromNL)
async def parse_natural_language(
    input_data: NaturalLanguageTaskInput
):
    """
    Parse natural language input into structured task data.
    
    Example inputs:
    - "Remind me to buy groceries tomorrow at 3pm"
    - "Urgent: Fix the login bug in production"
    - "研究一下新的AI框架，下周完成"
    """
    return await ai_service.parse_natural_language_task(input_data.text)


@router.post("/ai/create-from-text", response_model=TaskResponse)
async def create_task_from_natural_language(
    input_data: NaturalLanguageTaskInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a task from natural language input.
    Automatically parses and creates the task.
    """
    parsed = await ai_service.parse_natural_language_task(input_data.text)
    
    task_data = TaskCreate(
        title=parsed.title,
        description=parsed.description,
        priority=parsed.priority,
        tags=parsed.tags,
        status=TaskStatus.PENDING
    )
    
    task = await task_service.create_task(db, task_data, auto_suggest=False)
    
    # Store parsed tags as AI suggestions
    task.ai_suggested_tags = parsed.tags
    task.ai_suggested_priority = parsed.priority.value
    await db.commit()
    await db.refresh(task)
    
    return task


@router.post("/{task_id}/ai/suggest-tags", response_model=TagSuggestionResponse)
async def suggest_tags_for_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get AI-suggested tags for a task."""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    suggested_tags, reasoning = await ai_service.suggest_tags(
        task.title,
        task.description
    )
    
    # Update task with suggestions
    task.ai_suggested_tags = suggested_tags
    await db.commit()
    
    return TagSuggestionResponse(
        task_id=task_id,
        suggested_tags=suggested_tags,
        reasoning=reasoning
    )


@router.post("/{task_id}/ai/suggest-priority", response_model=PrioritySuggestionResponse)
async def suggest_priority_for_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get AI-suggested priority for a task."""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    suggested_priority, reasoning = await ai_service.suggest_priority(
        task.title,
        task.description
    )
    
    # Update task with suggestion
    task.ai_suggested_priority = suggested_priority.value
    await db.commit()
    
    return PrioritySuggestionResponse(
        task_id=task_id,
        suggested_priority=suggested_priority,
        reasoning=reasoning
    )


@router.post("/{task_id}/ai/breakdown", response_model=TaskBreakdownResponse)
async def breakdown_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Break down a complex task into subtasks.
    Uses AI to generate actionable subtasks.
    """
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    subtasks, reasoning = await ai_service.breakdown_task(
        task.title,
        task.description
    )
    
    return TaskBreakdownResponse(
        original_task_id=task_id,
        subtasks=subtasks,
        reasoning=reasoning
    )


@router.post("/ai/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(
    search_data: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search tasks using semantic similarity.
    Finds tasks related to the query by meaning, not just keywords.
    """
    results = await task_service.semantic_search(
        db,
        search_data.query,
        search_data.limit
    )
    
    search_results = [
        SemanticSearchResult(
            task=task,
            similarity_score=score
        )
        for task, score in results
    ]
    
    return SemanticSearchResponse(
        results=search_results,
        query=search_data.query
    )


@router.post("/ai/summary", response_model=TaskSummaryResponse)
async def get_task_summary(
    summary_request: TaskSummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an AI-generated summary of tasks.
    Includes statistics and actionable insights.
    """
    result = await task_service.get_task_summary(
        db,
        summary_request.task_ids,
        summary_request.period
    )
    
    return TaskSummaryResponse(**result)


@router.post("/ai/similar", response_model=SimilarTaskResponse)
async def find_similar_tasks(
    request: SimilarTaskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar tasks based on semantic similarity.
    Useful for detecting duplicate or related tasks.
    """
    task = await task_service.get_task(db, request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    similar_tasks = await task_service.find_similar_tasks(
        db, 
        request.task_id, 
        request.limit
    )
    
    results = [
        SimilarTaskResult(task=t, similarity_score=score)
        for t, score in similar_tasks
    ]
    
    return SimilarTaskResponse(
        source_task_id=request.task_id,
        similar_tasks=results
    )


@router.post("/ai/categorize", response_model=TaskCategoryResponse)
async def categorize_task(
    request: TaskCategoryRequest
):
    """
    Automatically categorize a task based on its content.
    Returns the main category, subcategories, and reasoning.
    """
    category, subcategories, reasoning = await ai_service.categorize_task(
        request.title,
        request.description
    )
    
    return TaskCategoryResponse(
        category=category,
        subcategories=subcategories,
        reasoning=reasoning
    )


@router.get("/ai/insights", response_model=TaskInsightsResponse)
async def get_task_insights(
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated insights and analytics about all tasks.
    Includes completion rate, status distribution, and recommendations.
    """
    return await task_service.get_task_insights(db)
