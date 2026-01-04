"""Task service for business logic."""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.ai_service import ai_service


class TaskService:
    """Service for task-related operations."""
    
    async def create_task(
        self,
        db: AsyncSession,
        task_data: TaskCreate,
        auto_suggest: bool = True
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            tags=task_data.tags
        )
        
        # Generate AI suggestions if enabled
        if auto_suggest:
            suggested_tags, _ = await ai_service.suggest_tags(
                task_data.title,
                task_data.description
            )
            suggested_priority, _ = await ai_service.suggest_priority(
                task_data.title,
                task_data.description
            )
            task.ai_suggested_tags = suggested_tags
            task.ai_suggested_priority = suggested_priority.value
            
            # Generate embedding for semantic search
            text = f"{task_data.title} {task_data.description or ''}"
            embedding = await ai_service.get_embedding(text)
            task.embedding = embedding
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    async def get_task(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    async def get_tasks(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Task], int]:
        """Get tasks with filtering, sorting, and pagination."""
        query = select(Task)
        count_query = select(func.count(Task.id))
        
        # Apply filters
        if status:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)
        
        if priority:
            query = query.where(Task.priority == priority)
            count_query = count_query.where(Task.priority == priority)
        
        if search:
            search_filter = or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Filter by tags in Python (JSON field)
        if tags:
            tasks = [t for t in tasks if any(tag in (t.tags or []) for tag in tags)]
        
        return list(tasks), total
    
    async def update_task(
        self,
        db: AsyncSession,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        task = await self.get_task(db, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Update embedding if title or description changed
        if "title" in update_data or "description" in update_data:
            text = f"{task.title} {task.description or ''}"
            task.embedding = await ai_service.get_embedding(text)
        
        await db.commit()
        await db.refresh(task)
        return task
    
    async def delete_task(self, db: AsyncSession, task_id: int) -> bool:
        """Delete a task."""
        task = await self.get_task(db, task_id)
        if not task:
            return False
        
        await db.delete(task)
        await db.commit()
        return True
    
    async def semantic_search(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10
    ) -> List[Tuple[Task, float]]:
        """Search tasks using semantic similarity."""
        # Get query embedding
        query_embedding = await ai_service.get_embedding(query)
        if not query_embedding:
            return []
        
        # Get all tasks with embeddings
        result = await db.execute(select(Task).where(Task.embedding.isnot(None)))
        tasks = result.scalars().all()
        
        # Compute similarities
        task_scores = []
        for task in tasks:
            if task.embedding:
                similarity = ai_service.compute_similarity(query_embedding, task.embedding)
                task_scores.append((task, similarity))
        
        # Sort by similarity and return top results
        task_scores.sort(key=lambda x: x[1], reverse=True)
        return task_scores[:limit]
    
    async def get_task_summary(
        self,
        db: AsyncSession,
        task_ids: Optional[List[int]] = None
    ) -> dict:
        """Get summary statistics and AI-generated summary for tasks."""
        if task_ids:
            result = await db.execute(select(Task).where(Task.id.in_(task_ids)))
        else:
            result = await db.execute(select(Task))
        
        tasks = result.scalars().all()
        
        # Calculate statistics
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        pending = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        high_priority = sum(1 for t in tasks if t.priority == TaskPriority.HIGH)
        
        # Generate AI summary
        task_dicts = [
            {"title": t.title, "status": t.status.value, "priority": t.priority.value}
            for t in tasks
        ]
        summary = await ai_service.summarize_tasks(task_dicts)
        
        return {
            "summary": summary,
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "high_priority_count": high_priority
        }


# Singleton instance
task_service = TaskService()

