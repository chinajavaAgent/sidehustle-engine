from fastapi import APIRouter
from typing import List
from models.schemas import (
    GeneratedContent, 
    ContentGenerationRequest, 
    ArticleFramework,
    ContentOptimizationRequest
)
from services.content_service import ContentService

router = APIRouter()
content_service = ContentService()

@router.post("/generate", response_model=GeneratedContent)
async def generate_content(request: ContentGenerationRequest):
    """生成文章内容"""
    return await content_service.generate_content(request)

@router.get("/frameworks", response_model=List[str])
async def get_frameworks():
    """获取所有文章框架"""
    return [framework.value for framework in ArticleFramework]

@router.post("/optimize/title", response_model=List[str])
async def optimize_title(title: str):
    """优化标题"""
    return await content_service.optimize_title(title)

@router.post("/optimize/polish")
async def polish_content(request: ContentOptimizationRequest):
    """内容润色"""
    if request.optimization_type == "polish":
        polished_content = await content_service.polish_content(request.content)
        return {"optimized_content": polished_content}
    else:
        return {"error": "Unsupported optimization type"}