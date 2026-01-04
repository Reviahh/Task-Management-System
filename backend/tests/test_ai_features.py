"""Unit tests for AI-powered features."""
import pytest
from httpx import AsyncClient


class TestNaturalLanguageParsing:
    """Test cases for natural language task parsing."""

    @pytest.mark.asyncio
    async def test_parse_simple_task(self, client: AsyncClient):
        """Test parsing a simple task description."""
        response = await client.post(
            "/api/tasks/ai/parse",
            json={"text": "Buy milk from the store"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "confidence" in data
        assert data["confidence"] >= 0 and data["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_parse_urgent_task(self, client: AsyncClient):
        """Test parsing an urgent task."""
        response = await client.post(
            "/api/tasks/ai/parse",
            json={"text": "紧急：修复生产环境的bug"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_parse_empty_text(self, client: AsyncClient):
        """Test parsing empty text."""
        response = await client.post(
            "/api/tasks/ai/parse",
            json={"text": ""}
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_from_natural_language(self, client: AsyncClient):
        """Test creating task from natural language."""
        response = await client.post(
            "/api/tasks/ai/create-from-text",
            json={"text": "下周完成项目报告"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data


class TestTagSuggestions:
    """Test cases for tag suggestions."""

    @pytest.mark.asyncio
    async def test_suggest_tags(self, client: AsyncClient, sample_task):
        """Test getting tag suggestions."""
        task_id = sample_task["id"]
        response = await client.post(f"/api/tasks/{task_id}/ai/suggest-tags")
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "suggested_tags" in data
        assert isinstance(data["suggested_tags"], list)

    @pytest.mark.asyncio
    async def test_suggest_tags_not_found(self, client: AsyncClient):
        """Test tag suggestions for non-existent task."""
        response = await client.post("/api/tasks/99999/ai/suggest-tags")
        
        assert response.status_code == 404


class TestPrioritySuggestions:
    """Test cases for priority suggestions."""

    @pytest.mark.asyncio
    async def test_suggest_priority(self, client: AsyncClient, sample_task):
        """Test getting priority suggestions."""
        task_id = sample_task["id"]
        response = await client.post(f"/api/tasks/{task_id}/ai/suggest-priority")
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "suggested_priority" in data
        assert data["suggested_priority"] in ["low", "medium", "high"]


class TestTaskBreakdown:
    """Test cases for task breakdown."""

    @pytest.mark.asyncio
    async def test_breakdown_task(self, client: AsyncClient, sample_task):
        """Test breaking down a task."""
        task_id = sample_task["id"]
        response = await client.post(f"/api/tasks/{task_id}/ai/breakdown")
        
        assert response.status_code == 200
        data = response.json()
        assert "original_task_id" in data
        assert "subtasks" in data
        assert isinstance(data["subtasks"], list)
        assert len(data["subtasks"]) >= 1


class TestSemanticSearch:
    """Test cases for semantic search."""

    @pytest.mark.asyncio
    async def test_semantic_search(self, client: AsyncClient, sample_task):
        """Test semantic search."""
        response = await client.post(
            "/api/tasks/ai/semantic-search",
            json={"query": "test", "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_semantic_search_empty_query(self, client: AsyncClient):
        """Test semantic search with empty query."""
        response = await client.post(
            "/api/tasks/ai/semantic-search",
            json={"query": ""}
        )
        
        assert response.status_code == 422


class TestTaskSummary:
    """Test cases for task summary."""

    @pytest.mark.asyncio
    async def test_get_summary(self, client: AsyncClient, sample_task):
        """Test getting task summary."""
        response = await client.post(
            "/api/tasks/ai/summary",
            json={}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "total_tasks" in data
        assert "completed_tasks" in data

    @pytest.mark.asyncio
    async def test_get_daily_summary(self, client: AsyncClient, sample_task):
        """Test getting daily task summary."""
        response = await client.post(
            "/api/tasks/ai/summary",
            json={"period": "daily"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


class TestTaskCategorization:
    """Test cases for task categorization."""

    @pytest.mark.asyncio
    async def test_categorize_task(self, client: AsyncClient):
        """Test task categorization."""
        response = await client.post(
            "/api/tasks/ai/categorize",
            json={
                "title": "去医院检查身体",
                "description": "年度体检"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "subcategories" in data

    @pytest.mark.asyncio
    async def test_categorize_work_task(self, client: AsyncClient):
        """Test categorizing a work-related task."""
        response = await client.post(
            "/api/tasks/ai/categorize",
            json={"title": "完成项目报告并提交给客户"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] in ["work", "other"]


class TestTaskInsights:
    """Test cases for task insights."""

    @pytest.mark.asyncio
    async def test_get_insights(self, client: AsyncClient, sample_task):
        """Test getting task insights."""
        response = await client.get("/api/tasks/ai/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "by_priority" in data
        assert "completion_rate" in data
        assert "insights" in data
        assert "recommendations" in data


class TestSimilarTasks:
    """Test cases for similar task detection."""

    @pytest.mark.asyncio
    async def test_find_similar_tasks(self, client: AsyncClient, sample_task):
        """Test finding similar tasks."""
        task_id = sample_task["id"]
        response = await client.post(
            "/api/tasks/ai/similar",
            json={"task_id": task_id, "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "source_task_id" in data
        assert "similar_tasks" in data
        assert isinstance(data["similar_tasks"], list)

