"""
FastAPI主应用
飞书GitHub机器人
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from .config import settings
from .api.webhook import router as webhook_router
from .api.health import router as health_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="飞书GitHub机器人",
    description="""
    🤖 **飞书GitHub机器人**
    
    这是一个用于将GitHub推送事件通知到飞书群的机器人服务。
    
    ## 功能特性
    
    - ✅ 接收GitHub推送事件
    - ✅ 发送美观的卡片消息到飞书群
    - ✅ 显示推送者、仓库、分支、提交信息
    - ✅ 支持GitHub Webhook签名验证
    - ✅ 支持飞书机器人签名验证
    - ✅ 提供测试接口和健康检查
    
    ## 使用方法
    
    1. 配置环境变量 `FEISHU_WEBHOOK_URL` 和 `FEISHU_SECRET`
    2. 在GitHub仓库中配置Webhook指向 `/github-webhook` 接口
    3. 使用 `/test` 接口测试飞书消息发送
    
    ## 接口说明
    
    - `/` - 服务状态检查
    - `/health` - 健康检查
    - `/test` - 测试飞书消息发送
    - `/github-webhook` - GitHub Webhook接收接口
    """,
    version="2.0.0",
    contact={
        "name": "飞书GitHub机器人",
        "url": "https://github.com/your-username/feishu-github-bot",
    },
    license_info={
        "name": "MIT",
    },
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router, tags=["健康检查"])
app.include_router(webhook_router, tags=["Webhook"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 飞书GitHub机器人启动中...")
    
    # 显示配置信息
    settings.display_config()
    
    # 验证配置
    if not settings.validate():
        logger.error("❌ 配置验证失败，请检查环境变量")
        sys.exit(1)
    
    logger.info("✅ 飞书GitHub机器人启动成功！")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 飞书GitHub机器人正在关闭...")


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 