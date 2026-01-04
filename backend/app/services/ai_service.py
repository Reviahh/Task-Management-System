"""AI Service for intelligent task features using OpenAI API."""
import json
import re
from typing import List, Optional, Tuple
from openai import AsyncOpenAI
from app.config import get_settings
from app.models.task import TaskPriority
from app.schemas.task import ParsedTaskFromNL, SubTask
import numpy as np

settings = get_settings()


class AIService:
    """AI service for task intelligence features."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        ) if settings.openai_api_key else None
        self.model = settings.openai_model
        self.embedding_model = "text-embedding-3-small"
    
    def _is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None and bool(settings.openai_api_key)
    
    async def parse_natural_language_task(self, text: str) -> ParsedTaskFromNL:
        """
        Parse natural language input into structured task data.
        Example: "Remind me to buy groceries tomorrow at 3pm" -> Task with title, due date, etc.
        """
        if not self._is_available():
            # Fallback: simple parsing without AI
            return self._fallback_parse(text)
        
        prompt = f"""You are a task parser. Parse the following natural language input into a structured task.
Extract:
1. title: A clear, concise task title
2. description: Additional details if any
3. priority: "low", "medium", or "high" based on urgency words (urgent, asap, important = high; when possible, someday = low)
4. tags: Relevant category tags (e.g., ["shopping", "personal"], ["work", "meeting"])
5. due_date: If mentioned (format: YYYY-MM-DD HH:MM or just YYYY-MM-DD)
6. confidence: Your confidence in the parsing (0.0 to 1.0)

Input: "{text}"

Respond ONLY with valid JSON in this exact format:
{{"title": "...", "description": "...", "priority": "medium", "tags": [], "due_date": null, "confidence": 0.9}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ParsedTaskFromNL(
                    title=data.get("title", text[:100]),
                    description=data.get("description"),
                    priority=TaskPriority(data.get("priority", "medium")),
                    tags=data.get("tags", []),
                    due_date=data.get("due_date"),
                    confidence=data.get("confidence", 0.8)
                )
        except Exception as e:
            print(f"AI parsing error: {e}")
        
        return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> ParsedTaskFromNL:
        """Fallback parsing when AI is not available."""
        # Simple heuristic parsing
        title = text[:100] if len(text) > 100 else text
        
        # Detect priority from keywords
        priority = TaskPriority.MEDIUM
        text_lower = text.lower()
        if any(word in text_lower for word in ["urgent", "asap", "important", "critical", "紧急", "重要"]):
            priority = TaskPriority.HIGH
        elif any(word in text_lower for word in ["someday", "maybe", "when possible", "低优先", "空闲"]):
            priority = TaskPriority.LOW
        
        # Simple tag extraction
        tags = []
        tag_keywords = {
            "work": ["work", "meeting", "project", "report", "工作", "会议"],
            "personal": ["personal", "home", "family", "个人", "家"],
            "shopping": ["buy", "shop", "purchase", "groceries", "购买", "购物"],
            "health": ["doctor", "gym", "exercise", "health", "健康", "运动"],
        }
        for tag, keywords in tag_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)
        
        return ParsedTaskFromNL(
            title=title,
            description=None,
            priority=priority,
            tags=tags,
            due_date=None,
            confidence=0.5
        )
    
    async def suggest_tags(self, title: str, description: Optional[str] = None) -> Tuple[List[str], str]:
        """Suggest tags for a task based on its content."""
        if not self._is_available():
            return self._fallback_suggest_tags(title, description)
        
        content = f"Title: {title}"
        if description:
            content += f"\nDescription: {description}"
        
        prompt = f"""Analyze this task and suggest 1-5 relevant tags.
Tags should be single words or short phrases, lowercase.

{content}

Respond ONLY with valid JSON:
{{"tags": ["tag1", "tag2"], "reasoning": "Brief explanation"}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("tags", [])[:5], data.get("reasoning", "")
        except Exception as e:
            print(f"Tag suggestion error: {e}")
        
        return self._fallback_suggest_tags(title, description)
    
    def _fallback_suggest_tags(self, title: str, description: Optional[str] = None) -> Tuple[List[str], str]:
        """Fallback tag suggestion."""
        text = (title + " " + (description or "")).lower()
        tags = []
        
        categories = {
            "development": ["code", "bug", "feature", "api", "database", "开发", "代码"],
            "meeting": ["meeting", "call", "discussion", "sync", "会议"],
            "documentation": ["doc", "write", "document", "readme", "文档"],
            "design": ["design", "ui", "ux", "mockup", "设计"],
            "testing": ["test", "qa", "quality", "测试"],
            "research": ["research", "investigate", "explore", "研究"],
        }
        
        for tag, keywords in categories.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        
        return tags[:5], "Based on keyword matching"
    
    async def suggest_priority(self, title: str, description: Optional[str] = None) -> Tuple[TaskPriority, str]:
        """Suggest priority for a task based on its content."""
        if not self._is_available():
            return self._fallback_suggest_priority(title, description)
        
        content = f"Title: {title}"
        if description:
            content += f"\nDescription: {description}"
        
        prompt = f"""Analyze this task and suggest an appropriate priority level.
Consider urgency, impact, and deadlines mentioned.

{content}

Respond ONLY with valid JSON:
{{"priority": "low|medium|high", "reasoning": "Brief explanation"}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                priority_str = data.get("priority", "medium").lower()
                priority = TaskPriority(priority_str) if priority_str in ["low", "medium", "high"] else TaskPriority.MEDIUM
                return priority, data.get("reasoning", "")
        except Exception as e:
            print(f"Priority suggestion error: {e}")
        
        return self._fallback_suggest_priority(title, description)
    
    def _fallback_suggest_priority(self, title: str, description: Optional[str] = None) -> Tuple[TaskPriority, str]:
        """Fallback priority suggestion."""
        text = (title + " " + (description or "")).lower()
        
        if any(word in text for word in ["urgent", "asap", "critical", "blocker", "紧急", "立即"]):
            return TaskPriority.HIGH, "Contains urgency keywords"
        elif any(word in text for word in ["someday", "maybe", "nice to have", "低优先"]):
            return TaskPriority.LOW, "Contains low-priority keywords"
        
        return TaskPriority.MEDIUM, "Default priority"
    
    async def breakdown_task(self, title: str, description: Optional[str] = None) -> Tuple[List[SubTask], str]:
        """Break down a complex task into subtasks."""
        if not self._is_available():
            return self._fallback_breakdown(title)
        
        content = f"Title: {title}"
        if description:
            content += f"\nDescription: {description}"
        
        prompt = f"""Break down this task into 3-7 actionable subtasks.
Each subtask should be specific, measurable, and achievable.

{content}

Respond ONLY with valid JSON:
{{"subtasks": [{{"title": "...", "description": "...", "estimated_effort": "15 min|1 hour|etc", "order": 1}}], "reasoning": "..."}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                subtasks = [
                    SubTask(
                        title=st.get("title", ""),
                        description=st.get("description"),
                        estimated_effort=st.get("estimated_effort"),
                        order=st.get("order", i + 1)
                    )
                    for i, st in enumerate(data.get("subtasks", []))
                ]
                return subtasks, data.get("reasoning", "")
        except Exception as e:
            print(f"Task breakdown error: {e}")
        
        return self._fallback_breakdown(title)
    
    def _fallback_breakdown(self, title: str) -> Tuple[List[SubTask], str]:
        """Fallback task breakdown."""
        subtasks = [
            SubTask(title=f"Plan: {title}", description="Define scope and requirements", estimated_effort="30 min", order=1),
            SubTask(title=f"Execute: {title}", description="Complete the main work", estimated_effort="2 hours", order=2),
            SubTask(title=f"Review: {title}", description="Review and verify completion", estimated_effort="30 min", order=3),
        ]
        return subtasks, "Generic breakdown without AI"
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get text embedding for semantic search."""
        if not self._is_available():
            return self._fallback_embedding(text)
        
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """
        Fallback embedding using simple TF-IDF-like approach.
        Returns a simple hash-based pseudo-embedding for basic similarity.
        """
        # Simple character-based embedding (not as good as real embeddings)
        words = text.lower().split()
        embedding = [0.0] * 256
        
        for word in words:
            for i, char in enumerate(word[:10]):
                idx = ord(char) % 256
                embedding[idx] += 1.0 / (i + 1)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (np.array(embedding) / norm).tolist()
        
        return embedding
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        if not embedding1 or not embedding2:
            return 0.0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Ensure same dimensions
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    async def summarize_tasks(self, tasks: List[dict]) -> str:
        """Generate a summary of tasks."""
        if not self._is_available() or not tasks:
            return self._fallback_summarize(tasks)
        
        task_list = "\n".join([
            f"- [{t['status']}] {t['title']} (Priority: {t['priority']})"
            for t in tasks[:20]  # Limit to 20 tasks
        ])
        
        prompt = f"""Summarize these tasks in a brief, actionable summary.
Include: overall status, priorities, and recommendations.

Tasks:
{task_list}

Provide a concise summary in 2-3 sentences."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Summary error: {e}")
        
        return self._fallback_summarize(tasks)
    
    def _fallback_summarize(self, tasks: List[dict]) -> str:
        """Fallback task summary."""
        if not tasks:
            return "No tasks to summarize."
        
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        high_priority = sum(1 for t in tasks if t.get("priority") == "high")
        
        return f"You have {total} tasks: {completed} completed, {total - completed} remaining. {high_priority} tasks are high priority."


# Singleton instance
ai_service = AIService()

