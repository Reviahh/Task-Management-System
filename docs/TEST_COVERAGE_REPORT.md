# Test Coverage Report

> **Generated:** 2026-01-04  
> **Platform:** Windows 32, Python 3.11.3-final-0  
> **Test Framework:** pytest 8.0.0

---

## Application Preview

### 主界面
![Dashboard](screenshots/dashboard.png)

### AI 功能
![AI Features](screenshots/ai-features.png)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Statements** | 797 |
| **Statements Covered** | 592 |
| **Statements Missed** | 205 |
| **Overall Coverage** | **74%** |
| **Tests Passed** | 32/32 |
| **Test Duration** | 307.09s (5:07) |

---

## Module Coverage Details

### Core Application

| Module | Statements | Missed | Coverage | Status |
|--------|------------|--------|----------|--------|
| `app/__init__.py` | 0 | 0 | 100% | ✅ |
| `app/config.py` | 14 | 0 | 100% | ✅ |
| `app/database.py` | 15 | 6 | 60% | ⚠️ |
| `app/logging_config.py` | 85 | 43 | 49% | ⚠️ |
| `app/main.py` | 74 | 17 | 77% | ✅ |

### Models

| Module | Statements | Missed | Coverage | Status |
|--------|------------|--------|----------|--------|
| `app/models/__init__.py` | 2 | 0 | 100% | ✅ |
| `app/models/task.py` | 27 | 1 | 96% | ✅ |

### Schemas

| Module | Statements | Missed | Coverage | Status |
|--------|------------|--------|----------|--------|
| `app/schemas/__init__.py` | 2 | 0 | 100% | ✅ |
| `app/schemas/task.py` | 103 | 0 | 100% | ✅ |

### Routes

| Module | Statements | Missed | Coverage | Status |
|--------|------------|--------|----------|--------|
| `app/routes/__init__.py` | 2 | 0 | 100% | ✅ |
| `app/routes/tasks.py` | 101 | 32 | 68% | ⚠️ |

### Services

| Module | Statements | Missed | Coverage | Status |
|--------|------------|--------|----------|--------|
| `app/services/__init__.py` | 3 | 0 | 100% | ✅ |
| `app/services/ai_service.py` | 244 | 52 | 79% | ✅ |
| `app/services/task_service.py` | 125 | 54 | 57% | ⚠️ |

---

## Uncovered Lines Analysis

### `app/database.py` (60%)
```
Missing: 28-32, 37-38
```
- Database initialization edge cases
- Connection error handling

### `app/logging_config.py` (49%)
```
Missing: 15-33, 45, 49, 61, 67, 70, 73, 85, 112-161
```
- JSON formatter edge cases
- Request logging middleware paths
- Structured logger utility methods

### `app/main.py` (77%)
```
Missing: 80-85, 181-184, 190, 198, 204-209
```
- Application lifespan shutdown handler
- Health check database error paths
- Readiness probe error response

### `app/models/task.py` (96%)
```
Missing: 61
```
- Model `__repr__` method

### `app/routes/tasks.py` (68%)
```
Missing: 43, 74-76, 92-94, 105-107, 117-119, 161-166, 176-179, 188, 202-205, 214, 231-234, 269, 303-306
```
- Error handling branches in CRUD operations
- Edge cases in AI endpoint handlers

### `app/services/ai_service.py` (79%)
```
Missing: 36, 60-65, 89, 115, 137-141, 170, 192-198, 209, 211, 218, 240-253, 271, 278, 307, 322, 329, 340, 357, 366, 383, 387-389, 398, 431-435, 471, 476, 507-508
```
- OpenAI API call paths (tested via fallback)
- Exception handling for external API failures

### `app/services/task_service.py` (57%)
```
Missing: 49-50, 55, 92-111, 121-131, 134-135, 140-145, 157, 161-168, 172, 186, 193-194, 197-200, 211, 231-241, 258, 268-271, 278, 291
```
- Complex query edge cases
- Embedding update logic
- Database transaction error handling

---

## Coverage by Category

```
Coverage Distribution:

100% ████████████████████ Config, Models, Schemas (7 modules)
 79% ████████████████     AI Service
 77% ███████████████      Main Application
 68% █████████████        Routes
 60% ████████████         Database
 57% ███████████          Task Service
 49% █████████            Logging
```

---

## Test Results

```
======================== test session starts =========================
platform win32 -- Python 3.11.3, pytest-8.0.0, pluggy-1.4.0
rootdir: D:\resource\creaition\backend
configfile: pytest.ini
plugins: anyio-4.2.0, asyncio-0.23.3, cov-4.1.0, html-4.1.1
asyncio: mode=auto
collected 32 items

tests/test_tasks.py::TestTaskCRUD::test_create_task PASSED
tests/test_tasks.py::TestTaskCRUD::test_create_task_minimal PASSED
tests/test_tasks.py::TestTaskCRUD::test_create_task_invalid PASSED
tests/test_tasks.py::TestTaskCRUD::test_get_tasks_empty PASSED
tests/test_tasks.py::TestTaskCRUD::test_get_tasks PASSED
tests/test_tasks.py::TestTaskCRUD::test_get_task_by_id PASSED
tests/test_tasks.py::TestTaskCRUD::test_get_task_not_found PASSED
tests/test_tasks.py::TestTaskCRUD::test_update_task PASSED
tests/test_tasks.py::TestTaskCRUD::test_delete_task PASSED
tests/test_tasks.py::TestTaskCRUD::test_delete_task_not_found PASSED
tests/test_tasks.py::TestTaskFiltering::test_filter_by_status PASSED
tests/test_tasks.py::TestTaskFiltering::test_filter_by_priority PASSED
tests/test_tasks.py::TestTaskFiltering::test_search_tasks PASSED
tests/test_tasks.py::TestTaskFiltering::test_pagination PASSED
tests/test_tasks.py::TestHealthCheck::test_health_check PASSED
tests/test_tasks.py::TestHealthCheck::test_root_endpoint PASSED
tests/test_ai_features.py::TestNaturalLanguageParsing::test_parse_simple_task PASSED
tests/test_ai_features.py::TestNaturalLanguageParsing::test_parse_urgent_task PASSED
tests/test_ai_features.py::TestNaturalLanguageParsing::test_parse_empty_text PASSED
tests/test_ai_features.py::TestNaturalLanguageParsing::test_create_from_natural_language PASSED
tests/test_ai_features.py::TestTagSuggestions::test_suggest_tags PASSED
tests/test_ai_features.py::TestTagSuggestions::test_suggest_tags_not_found PASSED
tests/test_ai_features.py::TestPrioritySuggestions::test_suggest_priority PASSED
tests/test_ai_features.py::TestTaskBreakdown::test_breakdown_task PASSED
tests/test_ai_features.py::TestSemanticSearch::test_semantic_search PASSED
tests/test_ai_features.py::TestSemanticSearch::test_semantic_search_empty_query PASSED
tests/test_ai_features.py::TestTaskSummary::test_get_summary PASSED
tests/test_ai_features.py::TestTaskSummary::test_get_daily_summary PASSED
tests/test_ai_features.py::TestTaskCategorization::test_categorize_task PASSED
tests/test_ai_features.py::TestTaskCategorization::test_categorize_work_task PASSED
tests/test_ai_features.py::TestTaskInsights::test_get_insights PASSED
tests/test_ai_features.py::TestSimilarTasks::test_find_similar_tasks PASSED

========================= 32 passed in 307.09s (0:05:07) =========================
```

---

## How to Run Tests

```bash
# Navigate to backend directory
cd backend

# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tasks.py -v
pytest tests/test_ai_features.py -v

# Generate HTML coverage report only
pytest --cov=app --cov-report=html:reports/coverage
```

---

## Reports Location

| Report | Path |
|--------|------|
| HTML Test Report | `backend/reports/test_report.html` |
| Coverage HTML Report | `backend/reports/coverage/index.html` |
| Coverage Terminal Output | Displayed during test run |

---

## Notes

- **AI Service Coverage (79%)**: Some OpenAI API code paths are not directly tested as they require external API calls. The fallback mechanisms are fully tested.
- **Logging Coverage (49%)**: Logging utilities have lower coverage as they're infrastructure code primarily exercised in production.
- **Task Service Coverage (57%)**: Some complex query paths and edge cases remain untested.

---

*Report generated by pytest-cov 4.1.0*

