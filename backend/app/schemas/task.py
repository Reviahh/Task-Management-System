"""Pydantic schemas for Task API."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, description="Task tags")


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    created_at: datetime
    updated_at: datetime
    ai_suggested_tags: List[str] = []
    ai_suggested_priority: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# AI-related schemas
class NaturalLanguageTaskInput(BaseModel):
    """Schema for natural language task creation."""
    text: str = Field(..., min_length=1, description="Natural language task description")


class ParsedTaskFromNL(BaseModel):
    """Schema for parsed task from natural language."""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = []
    due_date: Optional[str] = None
    confidence: float = Field(ge=0, le=1, description="Parsing confidence score")


class TaskBreakdownRequest(BaseModel):
    """Schema for task breakdown request."""
    task_id: int
    

class SubTask(BaseModel):
    """Schema for a subtask."""
    title: str
    description: Optional[str] = None
    estimated_effort: Optional[str] = None
    order: int


class TaskBreakdownResponse(BaseModel):
    """Schema for task breakdown response."""
    original_task_id: int
    subtasks: List[SubTask]
    reasoning: Optional[str] = None


class SemanticSearchRequest(BaseModel):
    """Schema for semantic search request."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")


class SemanticSearchResult(BaseModel):
    """Schema for semantic search result."""
    task: TaskResponse
    similarity_score: float = Field(ge=0, le=1)


class SemanticSearchResponse(BaseModel):
    """Schema for semantic search response."""
    results: List[SemanticSearchResult]
    query: str


class TagSuggestionResponse(BaseModel):
    """Schema for tag suggestion response."""
    task_id: int
    suggested_tags: List[str]
    reasoning: Optional[str] = None


class PrioritySuggestionResponse(BaseModel):
    """Schema for priority suggestion response."""
    task_id: int
    suggested_priority: TaskPriority
    reasoning: Optional[str] = None


class TaskSummaryRequest(BaseModel):
    """Schema for task summary request."""
    task_ids: Optional[List[int]] = None
    period: Optional[str] = Field(None, description="Period: 'daily', 'weekly', 'all'")


class TaskSummaryResponse(BaseModel):
    """Schema for task summary response."""
    summary: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    high_priority_count: int

