"""
iTick MCP Server Configuration
配置管理模块，从环境变量和 .env 文件加载配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # iTick API 配置
    itick_api_key: str = ""
    itick_api_base_url: str = "https://api.itick.org"
    
    # 服务器配置
    port: int = 3000
    host: str = "0.0.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_itick_api_key() -> str:
    """
    获取 iTick API Key，优先级：
    1. 请求 Header 中的 X-Itick-Token
    2. 环境变量 ITICK_API_KEY
    """
    if not settings.itick_api_key:
        raise ValueError(
            "iTick API Key 未配置！请设置环境变量 ITICK_API_KEY 或在请求头中传递 X-Itick-Token"
        )
    return settings.itick_api_key
