import asyncio
import random
from typing import List
from models.schemas import Topic, TopicCategory

class TopicService:
    def __init__(self):
        # 模拟数据源
        self.mock_topics = [
            Topic(
                id=1,
                title="AI绘画接单，月入过万的新兴副业",
                reason="近期AI绘画工具火爆，Midjourney、Stable Diffusion等工具降低创作门槛",
                category=TopicCategory.AI_TOOLS,
                heat=85,
                keywords=["AI绘画", "Midjourney", "副业", "设计"],
            ),
            Topic(
                id=2,
                title="闲鱼卖货实战指南：从0到月收入5000+",
                reason="闲鱼平台用户活跃，二手交易市场需求旺盛",
                category=TopicCategory.E_COMMERCE,
                heat=78,
                keywords=["闲鱼", "二手交易", "电商", "卖货"],
            ),
            Topic(
                id=3,
                title="短视频剪辑接私活，学生党也能月入3000",
                reason="短视频内容需求激增，剪辑技能门槛适中",
                category=TopicCategory.CONTENT_CREATION,
                heat=72,
                keywords=["短视频", "剪辑", "私活", "学生"],
            ),
            Topic(
                id=4,
                title="小红书种草文案写作，单篇收费200+",
                reason="品牌营销需求大增，种草文案市场火热",
                category=TopicCategory.CONTENT_CREATION,
                heat=69,
                keywords=["小红书", "种草", "文案", "营销"],
            ),
            Topic(
                id=5,
                title="微信表情包制作，躺赚被动收入",
                reason="表情包使用频次高，制作门槛低",
                category=TopicCategory.CONTENT_CREATION,
                heat=65,
                keywords=["表情包", "微信", "被动收入", "设计"],
            ),
            Topic(
                id=6,
                title="线上英语陪练，时薪100+的技能变现",
                reason="在线教育需求持续增长，语言学习市场庞大",
                category=TopicCategory.SKILL_MONETIZATION,
                heat=61,
                keywords=["英语", "陪练", "在线教育", "技能变现"],
            ),
        ]
    
    async def get_trending_topics(self, limit: int = 10) -> List[Topic]:
        """获取热门选题"""
        # 模拟异步处理
        await asyncio.sleep(1)
        
        # 随机打乱并返回指定数量
        topics = random.sample(self.mock_topics, min(limit, len(self.mock_topics)))
        return sorted(topics, key=lambda x: x.heat, reverse=True)
    
    async def search_topics_by_keyword(self, keyword: str) -> List[Topic]:
        """根据关键词搜索选题"""
        await asyncio.sleep(0.5)
        
        filtered_topics = []
        for topic in self.mock_topics:
            if (keyword.lower() in topic.title.lower() or 
                keyword.lower() in topic.reason.lower() or
                any(keyword.lower() in kw.lower() for kw in topic.keywords)):
                filtered_topics.append(topic)
        
        return filtered_topics
    
    async def get_topics_by_category(self, category: TopicCategory) -> List[Topic]:
        """根据分类获取选题"""
        await asyncio.sleep(0.3)
        
        return [topic for topic in self.mock_topics if topic.category == category]