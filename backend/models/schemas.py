from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TopicCategory(str, Enum):
    AI_TOOLS = "AI工具"
    E_COMMERCE = "电商变现"
    CONTENT_CREATION = "内容创作"
    SKILL_MONETIZATION = "技能变现"
    INVESTMENT = "投资理财"
    FREELANCE = "自由职业"

class Topic(BaseModel):
    id: int
    title: str
    reason: str
    category: TopicCategory
    heat: int
    keywords: List[str] = []
    source_url: Optional[str] = None

class ArticleFramework(str, Enum):
    PROBLEM_SOLUTION = "痛点+解决方案型"
    STORY_TIPS = "故事+干货型"
    TUTORIAL_STEPS = "教程+步骤型"
    COMPARISON_REVIEW = "盘点+评测型"

class ContentGenerationRequest(BaseModel):
    topic: Topic
    framework: ArticleFramework
    style: str = "轻松活泼"
    word_count: int = 2000

class GeneratedContent(BaseModel):
    title: str
    content: str
    outline: List[str]
    keywords: List[str]
    estimated_read_time: int

class ContentOptimizationRequest(BaseModel):
    content: str
    optimization_type: str  # "title", "polish", "format"