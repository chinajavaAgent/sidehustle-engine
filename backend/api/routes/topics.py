from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from models.schemas import Topic, TopicCategory
from services.topic_service import TopicService
from services.intelligent_topic_service import IntelligentTopicService

router = APIRouter()
topic_service = TopicService()
intelligent_service = IntelligentTopicService()

class WeChatAnalysisRequest(BaseModel):
    urls: List[str]
    limit: Optional[int] = 10

class SingleArticleRequest(BaseModel):
    url: str

@router.get("/trending", response_model=List[Topic])
async def get_trending_topics(limit: int = Query(10, ge=1, le=50)):
    """获取热门选题（传统方式）"""
    return await topic_service.get_trending_topics(limit)

@router.post("/trending/wechat", response_model=List[Topic])
async def get_trending_topics_from_wechat(request: WeChatAnalysisRequest):
    """基于微信公众号文章获取热门选题"""
    try:
        if not request.urls:
            raise HTTPException(status_code=400, detail="URLs列表不能为空")
        
        topics = await intelligent_service.get_trending_topics_from_wechat(
            request.urls, request.limit
        )
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取选题失败: {str(e)}")

@router.post("/analyze/article")
async def analyze_single_article(request: SingleArticleRequest):
    """分析单篇微信文章"""
    try:
        result = await intelligent_service.analyze_single_article(request.url)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析文章失败: {str(e)}")

@router.post("/analyze/batch")
async def batch_analyze_articles(request: WeChatAnalysisRequest):
    """批量分析多篇微信文章"""
    try:
        if not request.urls:
            raise HTTPException(status_code=400, detail="URLs列表不能为空")
        
        if len(request.urls) > 10:
            raise HTTPException(status_code=400, detail="单次最多分析10篇文章")
        
        result = await intelligent_service.batch_analyze_articles(request.urls)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

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

@router.get("/demo/wechat")
async def demo_wechat_analysis():
    """演示微信文章分析功能"""
    demo_url = "https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ"
    
    try:
        # 使用您提供的URL作为演示
        topics = await intelligent_service.get_trending_topics_from_wechat([demo_url], 5)
        
        return {
            "message": "微信文章分析演示",
            "source_url": demo_url,
            "generated_topics": [topic.dict() for topic in topics],
            "note": "由于微信的反爬限制，实际结果可能使用备用数据"
        }
    except Exception as e:
        return {
            "message": "演示功能",
            "error": str(e),
            "fallback_topics": [
                {
                    "title": "基于微信公众号的副业内容分析",
                    "reason": "通过分析热门公众号文章，提取副业机会和趋势",
                    "category": "内容创作",
                    "heat": 75
                }
            ]
        }