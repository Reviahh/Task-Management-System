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
    
    async def summarize_tasks(self, tasks: List[dict], period: Optional[str] = None) -> str:
        """Generate a summary of tasks."""
        if not self._is_available() or not tasks:
            return self._fallback_summarize(tasks)
        
        task_list = "\n".join([
            f"- [{t['status']}] {t['title']} (优先级: {t['priority']})"
            for t in tasks[:20]  # Limit to 20 tasks
        ])
        
        period_text = ""
        if period == "daily":
            period_text = "今天的"
        elif period == "weekly":
            period_text = "本周的"
        
        prompt = f"""请用中文总结{period_text}这些任务，提供简洁的、可操作的摘要。
包括：整体状态、优先事项、以及建议。

任务列表：
{task_list}

请用2-3句话提供摘要，使用中文回复。"""
        
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
            return "暂无任务需要总结。"
        
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        high_priority = sum(1 for t in tasks if t.get("priority") == "high")
        
        return f"您共有 {total} 个任务：{completed} 个已完成，{in_progress} 个进行中，{pending} 个待处理。其中 {high_priority} 个是高优先级任务。"

    async def find_similar_tasks(self, task_title: str, task_description: Optional[str], 
                                  all_tasks: List[dict], limit: int = 5) -> List[Tuple[dict, float]]:
        """Find similar tasks based on content similarity."""
        query_text = f"{task_title} {task_description or ''}"
        query_embedding = await self.get_embedding(query_text)
        
        if not query_embedding:
            return []
        
        similarities = []
        for task in all_tasks:
            if task.get("embedding"):
                similarity = self.compute_similarity(query_embedding, task["embedding"])
                similarities.append((task, similarity))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    async def categorize_task(self, title: str, description: Optional[str] = None) -> Tuple[str, List[str], str]:
        """Automatically categorize a task into predefined categories."""
        if not self._is_available():
            return self._fallback_categorize(title, description)
        
        content = f"Title: {title}"
        if description:
            content += f"\nDescription: {description}"
        
        prompt = f"""Analyze this task and categorize it.

{content}

Categories to choose from:
- work: 工作相关任务
- personal: 个人事务
- health: 健康和运动
- finance: 财务相关
- learning: 学习和成长
- social: 社交活动
- home: 家庭事务
- creative: 创意项目
- urgent: 紧急事项
- other: 其他

Respond ONLY with valid JSON:
{{"category": "work", "subcategories": ["meeting", "project"], "reasoning": "This task is about..."}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return (
                    data.get("category", "other"),
                    data.get("subcategories", []),
                    data.get("reasoning", "")
                )
        except Exception as e:
            print(f"Categorization error: {e}")
        
        return self._fallback_categorize(title, description)
    
    def _fallback_categorize(self, title: str, description: Optional[str] = None) -> Tuple[str, List[str], str]:
        """Fallback task categorization."""
        text = (title + " " + (description or "")).lower()
        
        category_keywords = {
            "work": ["work", "meeting", "project", "report", "client", "deadline", "工作", "会议", "项目", "报告", "客户", "截止", "办公", "汇报", "同事", "老板", "公司"],
            "personal": ["personal", "self", "个人", "自己", "私人"],
            "health": ["health", "gym", "exercise", "doctor", "hospital", "medicine", "健康", "运动", "医生", "锻炼", "医院", "检查", "体检", "药", "治疗", "看病", "身体"],
            "finance": ["money", "pay", "bill", "budget", "invest", "bank", "钱", "支付", "账单", "投资", "银行", "财务", "工资", "转账", "理财"],
            "learning": ["learn", "study", "course", "book", "read", "tutorial", "学习", "课程", "阅读", "教程", "培训", "知识", "技能"],
            "social": ["friend", "party", "dinner", "meet", "朋友", "聚会", "约会", "聚餐", "社交", "见面"],
            "home": ["home", "clean", "repair", "house", "家", "打扫", "修理", "整理", "家务", "房间", "装修"],
            "creative": ["design", "create", "art", "write", "设计", "创作", "艺术", "写作", "画"],
            "urgent": ["urgent", "asap", "emergency", "important", "critical", "紧急", "立即", "马上", "重要", "尽快"],
            "shopping": ["buy", "shop", "purchase", "order", "购买", "购物", "买", "下单", "商城"],
        }
        
        matched_categories = []
        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                matched_categories.append(category)
        
        if matched_categories:
            # Return first match as primary, rest as subcategories
            return matched_categories[0], matched_categories[1:3], f"基于关键词匹配: {matched_categories[0]}"
        
        return "other", [], "未能匹配到具体分类"

    async def generate_task_insights(self, tasks: List[dict]) -> dict:
        """Generate insights and analytics about tasks."""
        if not tasks:
            return {
                "total": 0,
                "insights": [],
                "recommendations": []
            }
        
        # Basic statistics
        total = len(tasks)
        by_status = {}
        by_priority = {}
        by_tag = {}
        
        for task in tasks:
            status = task.get("status", "pending")
            priority = task.get("priority", "medium")
            tags = task.get("tags", [])
            
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            for tag in tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1
        
        insights = []
        recommendations = []
        
        # Generate insights
        if by_status.get("pending", 0) > total * 0.5:
            insights.append("超过一半的任务仍在待处理状态")
            recommendations.append("建议优先处理积压的任务")
        
        if by_priority.get("high", 0) > 3:
            insights.append(f"您有 {by_priority.get('high', 0)} 个高优先级任务")
            recommendations.append("考虑先完成高优先级任务")
        
        completion_rate = by_status.get("completed", 0) / total * 100 if total > 0 else 0
        insights.append(f"任务完成率: {completion_rate:.1f}%")
        
        if by_tag:
            top_tags = sorted(by_tag.items(), key=lambda x: x[1], reverse=True)[:3]
            insights.append(f"最常用的标签: {', '.join([t[0] for t in top_tags])}")
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_tag": by_tag,
            "completion_rate": completion_rate,
            "insights": insights,
            "recommendations": recommendations
        }


# Singleton instance
ai_service = AIService()

