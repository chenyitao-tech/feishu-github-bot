from fastapi import APIRouter, HTTPException
import logging

from app.models import HealthCheck, APIResponse
from app.services.feishu import feishu_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def root():
    return HealthCheck()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck()


@router.get("/test", response_model=APIResponse)
async def test_feishu():
    try:
        # 检查配置
        if not settings.feishu_webhook_url:
            raise HTTPException(
                status_code=500, 
                detail="飞书webhook地址未配置"
            )
        # 创建测试卡片
        test_card = feishu_service.create_test_card()
        # 发送测试消息
        if feishu_service.send_card_message(test_card):
            logger.info("测试消息发送成功")
            return APIResponse(
                status="success",
                message="测试消息发送成功，请检查飞书群"
            )
        else:
            logger.error("测试消息发送失败")
            raise HTTPException(
                status_code=500,
                detail="测试消息发送失败，请检查飞书机器人配置"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试接口异常: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 