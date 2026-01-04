"""Unit tests for task API endpoints."""
import pytest
from httpx import AsyncClient


class TestTaskCRUD:
    """Test cases for task CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient):
        """Test creating a new task."""
        response = await client.post(
            "/api/tasks/",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "medium",
                "tags": ["shopping"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["priority"] == "medium"
        assert "shopping" in data["tags"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, client: AsyncClient):
        """Test creating a task with minimal fields."""
        response = await client.post(
            "/api/tasks/",
            json={"title": "Minimal task"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal task"
        assert data["priority"] == "medium"  # default
        assert data["status"] == "pending"  # default

    @pytest.mark.asyncio
    async def test_create_task_invalid(self, client: AsyncClient):
        """Test creating a task with invalid data."""
        response = await client.post(
            "/api/tasks/",
            json={"title": ""}  # Empty title should fail
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, client: AsyncClient):
        """Test getting tasks when none exist."""
        response = await client.get("/api/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_tasks(self, client: AsyncClient, sample_task):
        """Test getting task list."""
        response = await client.get("/api/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) >= 1
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, client: AsyncClient, sample_task):
        """Test getting a specific task."""
        task_id = sample_task["id"]
        response = await client.get(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task["title"]

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting a non-existent task."""
        response = await client.get("/api/tasks/99999")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, sample_task):
        """Test updating a task."""
        task_id = sample_task["id"]
        response = await client.put(
            f"/api/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "status": "in_progress",
                "priority": "high"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, sample_task):
        """Test deleting a task."""
        task_id = sample_task["id"]
        response = await client.delete(f"/api/tasks/{task_id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client: AsyncClient):
        """Test deleting a non-existent task."""
        response = await client.delete("/api/tasks/99999")
        
        assert response.status_code == 404


class TestTaskFiltering:
    """Test cases for task filtering and sorting."""

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client: AsyncClient, sample_task):
        """Test filtering tasks by status."""
        response = await client.get("/api/tasks/?status=pending")
        
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "pending"

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client: AsyncClient, sample_task):
        """Test filtering tasks by priority."""
        response = await client.get("/api/tasks/?priority=medium")
        
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_search_tasks(self, client: AsyncClient, sample_task):
        """Test searching tasks."""
        response = await client.get("/api/tasks/?search=Test")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) >= 1

    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient):
        """Test task pagination."""
        # Create multiple tasks
        for i in range(5):
            await client.post(
                "/api/tasks/",
                json={"title": f"Task {i}"}
            )
        
        response = await client.get("/api/tasks/?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2


class TestHealthCheck:
    """Test cases for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "ai_service" in data["checks"]

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

