from fastapi import APIRouter, Query
from typing import List, Optional
from models.schemas import Topic, TopicCategory
from services.topic_service import TopicService

router = APIRouter()
topic_service = TopicService()

@router.get("/trending", response_model=List[Topic])
async def get_trending_topics(limit: int = Query(10, ge=1, le=50)):
    """获取热门选题"""
    return await topic_service.get_trending_topics(limit)

@router.get("/search", response_model=List[Topic])
async def search_topics(keyword: str = Query(..., min_length=1)):
    """根据关键词搜索选题"""
    return await topic_service.search_topics_by_keyword(keyword)

@router.get("/category/{category}", response_model=List[Topic])
async def get_topics_by_category(category: TopicCategory):
    """根据分类获取选题"""
    return await topic_service.get_topics_by_category(category)

@router.get("/categories", response_model=List[str])
async def get_categories():
    """获取所有分类"""
    return [category.value for category in TopicCategory]