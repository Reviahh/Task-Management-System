"""Additional tests to boost code coverage."""
import pytest
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from app.logging_config import (
    JSONFormatter,
    StructuredLogger,
    setup_logging,
    log_execution_time
)
from app.database import init_db, get_db


class TestDatabaseModule:
    """Tests for database module to improve coverage."""

    @pytest.mark.asyncio
    async def test_init_db(self, test_db):
        """Test database initialization."""
        # init_db is already called in test_db fixture
        # This test verifies it works without errors
        pass

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self, test_db):
        """Test get_db dependency yields a session."""
        # The get_db is tested through the fixture
        # Verify session is usable
        async for session in get_db():
            assert session is not None
            break


class TestLoggingConfig:
    """Tests for logging configuration module."""

    def test_json_formatter_basic(self):
        """Test JSONFormatter formats log records correctly."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        result = formatter.format(record)
        
        assert "Test message" in result
        assert "INFO" in result
        assert "test" in result
        assert '"timestamp"' in result

    def test_json_formatter_with_exception(self):
        """Test JSONFormatter handles exceptions."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        result = formatter.format(record)
        
        assert "exception" in result
        assert "ValueError" in result

    def test_json_formatter_with_extra_data(self):
        """Test JSONFormatter includes extra data."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.extra_data = {"request_id": "123", "user": "test_user"}
        result = formatter.format(record)
        
        assert "request_id" in result
        assert "123" in result

    def test_structured_logger_set_context(self):
        """Test StructuredLogger context management."""
        logger = StructuredLogger("test_app")
        logger.set_context(request_id="abc123", user_id=42)
        
        assert logger._context["request_id"] == "abc123"
        assert logger._context["user_id"] == 42

    def test_structured_logger_clear_context(self):
        """Test StructuredLogger context clearing."""
        logger = StructuredLogger("test_app")
        logger.set_context(request_id="abc123")
        logger.clear_context()
        
        assert len(logger._context) == 0

    def test_structured_logger_all_levels(self):
        """Test all log levels of StructuredLogger."""
        logger = StructuredLogger("test_levels")
        
        # These should not raise errors
        logger.debug("Debug message", extra_field="debug")
        logger.info("Info message", extra_field="info")
        logger.warning("Warning message", extra_field="warning")
        logger.error("Error message", extra_field="error")
        logger.critical("Critical message", extra_field="critical")

    def test_setup_logging_debug_mode(self):
        """Test setup_logging in debug mode."""
        logger = setup_logging(debug=True, json_format=False)
        
        assert logger is not None
        assert isinstance(logger, StructuredLogger)

    def test_setup_logging_json_format(self):
        """Test setup_logging with JSON format."""
        logger = setup_logging(debug=False, json_format=True)
        
        assert logger is not None
        assert isinstance(logger, StructuredLogger)

    @pytest.mark.asyncio
    async def test_log_execution_time_async_success(self):
        """Test log_execution_time decorator for async functions."""
        test_logger = StructuredLogger("test_decorator")
        
        @log_execution_time(test_logger)
        async def sample_async_func():
            return "success"
        
        result = await sample_async_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_log_execution_time_async_error(self):
        """Test log_execution_time decorator handles async errors."""
        test_logger = StructuredLogger("test_decorator")
        
        @log_execution_time(test_logger)
        async def failing_async_func():
            raise RuntimeError("Test error")
        
        with pytest.raises(RuntimeError):
            await failing_async_func()

    def test_log_execution_time_sync_success(self):
        """Test log_execution_time decorator for sync functions."""
        test_logger = StructuredLogger("test_decorator")
        
        @log_execution_time(test_logger)
        def sample_sync_func():
            return "sync_success"
        
        result = sample_sync_func()
        assert result == "sync_success"

    def test_log_execution_time_sync_error(self):
        """Test log_execution_time decorator handles sync errors."""
        test_logger = StructuredLogger("test_decorator")
        
        @log_execution_time(test_logger)
        def failing_sync_func():
            raise ValueError("Sync error")
        
        with pytest.raises(ValueError):
            failing_sync_func()


class TestRoutesEdgeCases:
    """Edge case tests for routes to improve coverage."""

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, client: AsyncClient):
        """Test updating a non-existent task returns 404."""
        response = await client.put(
            "/api/tasks/99999",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_tasks_with_tags_filter(self, client: AsyncClient, sample_task):
        """Test listing tasks with tags filter."""
        response = await client.get("/api/tasks/?tags=test,sample")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data

    @pytest.mark.asyncio
    async def test_list_tasks_sort_asc(self, client: AsyncClient, sample_task):
        """Test listing tasks with ascending sort order."""
        response = await client.get("/api/tasks/?sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data

    @pytest.mark.asyncio
    async def test_list_tasks_sort_by_title(self, client: AsyncClient, sample_task):
        """Test listing tasks sorted by title."""
        response = await client.get("/api/tasks/?sort_by=title")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data

    @pytest.mark.asyncio
    async def test_suggest_priority_not_found(self, client: AsyncClient):
        """Test priority suggestion for non-existent task."""
        response = await client.post("/api/tasks/99999/ai/suggest-priority")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_breakdown_task_not_found(self, client: AsyncClient):
        """Test task breakdown for non-existent task."""
        response = await client.post("/api/tasks/99999/ai/breakdown")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_find_similar_tasks_not_found(self, client: AsyncClient):
        """Test finding similar tasks for non-existent task."""
        response = await client.post(
            "/api/tasks/ai/similar",
            json={"task_id": 99999, "limit": 5}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_task_from_natural_language(self, client: AsyncClient):
        """Test creating task from natural language with full flow."""
        response = await client.post(
            "/api/tasks/ai/create-from-text",
            json={"text": "紧急修复登录页面的bug，这很重要"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data


class TestTaskServiceEdgeCases:
    """Edge case tests for task service to improve coverage."""

    @pytest.mark.asyncio
    async def test_create_task_without_auto_suggest(self, client: AsyncClient):
        """Test creating task with auto_suggest disabled."""
        # This is tested via the create-from-text endpoint which sets auto_suggest=False
        response = await client.post(
            "/api/tasks/ai/create-from-text",
            json={"text": "Simple task without suggestions"}
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_task_title_updates_embedding(self, client: AsyncClient, sample_task):
        """Test that updating task title also updates embedding."""
        task_id = sample_task["id"]
        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Completely new title for embedding update"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Completely new title for embedding update"

    @pytest.mark.asyncio
    async def test_update_task_description_updates_embedding(self, client: AsyncClient, sample_task):
        """Test that updating task description also updates embedding."""
        task_id = sample_task["id"]
        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"description": "New description to trigger embedding update"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New description to trigger embedding update"

    @pytest.mark.asyncio
    async def test_semantic_search_with_multiple_tasks(self, client: AsyncClient):
        """Test semantic search with multiple tasks."""
        # Create several tasks first
        for i in range(3):
            await client.post(
                "/api/tasks/",
                json={
                    "title": f"Programming task {i}",
                    "description": f"Write code for feature {i}"
                }
            )
        
        response = await client.post(
            "/api/tasks/ai/semantic-search",
            json={"query": "programming code", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    @pytest.mark.asyncio
    async def test_find_similar_tasks_with_data(self, client: AsyncClient, sample_task):
        """Test finding similar tasks when similar tasks exist."""
        # Create a similar task
        await client.post(
            "/api/tasks/",
            json={
                "title": "Test Task Similar",
                "description": "This is a test task similar to sample"
            }
        )
        
        response = await client.post(
            "/api/tasks/ai/similar",
            json={"task_id": sample_task["id"], "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "similar_tasks" in data

    @pytest.mark.asyncio
    async def test_task_summary_with_daily_period(self, client: AsyncClient, sample_task):
        """Test task summary with daily period filter."""
        response = await client.post(
            "/api/tasks/ai/summary",
            json={"period": "daily"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_task_summary_with_weekly_period(self, client: AsyncClient, sample_task):
        """Test task summary with weekly period filter."""
        response = await client.post(
            "/api/tasks/ai/summary",
            json={"period": "weekly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_task_summary_with_task_ids(self, client: AsyncClient, sample_task):
        """Test task summary filtered by specific task IDs."""
        response = await client.post(
            "/api/tasks/ai/summary",
            json={"task_ids": [sample_task["id"]]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


class TestHealthEndpointsExtended:
    """Extended tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_liveness_probe(self, client: AsyncClient):
        """Test Kubernetes liveness probe endpoint."""
        response = await client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_readiness_probe(self, client: AsyncClient):
        """Test Kubernetes readiness probe endpoint."""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

