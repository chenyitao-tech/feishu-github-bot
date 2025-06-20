from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import logging

from app.models import GitHubWebhookPayload, APIResponse
from app.services.github import github_service
from app.services.feishu import feishu_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/github-webhook", response_model=APIResponse)
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    处理GitHub webhook请求
    - **x_github_event**: GitHub事件类型
    - **x_hub_signature_256**: GitHub签名
    """
    try:
        # 获取原始请求体用于签名验证
        body = await request.body()
        # 验证GitHub签名
        if not github_service.verify_signature(body, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
        # 检查是否为推送事件
        if not github_service.is_push_event(x_github_event):
            logger.info(f"忽略非推送事件: {x_github_event}")
            return APIResponse(
                status="ignored", 
                message=f"Event type '{x_github_event}' is not supported"
            )
        # 解析JSON数据
        payload_data = await request.json()
        # 检查是否应该忽略此推送
        if github_service.should_ignore_push(payload_data):
            return APIResponse(
                status="ignored", 
                message="Push event ignored based on filter rules"
            )
        # 验证和解析payload
        try:
            payload = GitHubWebhookPayload(**payload_data)
        except Exception as e:
            logger.error(f"Invalid payload format: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload format")
        # 创建推送通知卡片
        card = feishu_service.create_push_card(payload)
        # 发送到飞书
        if feishu_service.send_card_message(card):
            logger.info(f"成功处理GitHub推送: {payload.repository.full_name}")
            return APIResponse(
                status="success", 
                message="Push notification sent successfully"
            )
        else:
            logger.error("发送飞书消息失败")
            raise HTTPException(status_code=500, detail="Failed to send notification")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理GitHub webhook异常: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 