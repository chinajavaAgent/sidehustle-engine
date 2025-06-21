from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import topics, content
from core.config import settings

app = FastAPI(
    title="副业有道内容引擎 API",
    description="自动化内容生产系统后端服务",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(content.router, prefix="/api/content", tags=["content"])

@app.get("/")
async def root():
    return {"message": "副业有道内容引擎 API 服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)