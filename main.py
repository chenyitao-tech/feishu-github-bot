#!/usr/bin/env python3
"""
飞书GitHub机器人 - FastAPI版本
入口文件
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    # 启动FastAPI服务
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 