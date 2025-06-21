#!/usr/bin/env python3
"""
SideHustle Engine API 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import topics, content

app = FastAPI(
    title="SideHustle Engine API",
    description="副业有道内容引擎 - RPA多平台内容分析API",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "SideHustle Engine API",
        "version": "1.0.0",
        "description": "副业有道内容引擎 - RPA多平台内容分析",
        "features": [
            "多平台趋势分析 (Google, YouTube, Reddit)",
            "RPA网页自动化数据获取",
            "智能内容洞察生成",
            "影响者分析",
            "内容空白识别"
        ],
        "docs": "/docs",
        "endpoints": {
            "trending_analysis": "/api/topics/trending/rpa-analysis",
            "content_gaps": "/api/topics/insights/content-gaps",
            "influencers": "/api/topics/insights/influencers",
            "system_status": "/api/topics/rpa/status"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "sidehustle-engine-api"}