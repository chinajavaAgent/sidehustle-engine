from typing import Optional

class Settings:
    # API配置
    api_title: str = "副业有道内容引擎"
    api_version: str = "1.0.0"
    
    # OpenAI配置
    openai_api_key: Optional[str] = None

settings = Settings()