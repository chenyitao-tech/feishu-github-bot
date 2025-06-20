from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GitHubCommit(BaseModel):
    """GitHub提交信息模型"""
    message: str
    url: Optional[str] = None
    author: Optional[Dict[str, Any]] = None


class GitHubRepository(BaseModel):
    """GitHub仓库信息模型"""
    full_name: str
    html_url: Optional[str] = None
    name: Optional[str] = None


class GitHubPusher(BaseModel):
    """GitHub推送者信息模型"""
    name: str
    email: Optional[str] = None


class GitHubWebhookPayload(BaseModel):
    """GitHub Webhook载荷模型"""
    ref: str
    repository: GitHubRepository
    pusher: GitHubPusher
    commits: List[GitHubCommit]
    before: Optional[str] = None
    after: Optional[str] = None


class FeishuTextContent(BaseModel):
    """飞书文本内容模型"""
    text: str


class FeishuTextMessage(BaseModel):
    """飞书文本消息模型"""
    msg_type: str = "text"
    content: FeishuTextContent
    timestamp: Optional[str] = None
    sign: Optional[str] = None


class FeishuCardElement(BaseModel):
    """飞书卡片元素模型"""
    tag: str
    text: Optional[Dict[str, str]] = None
    fields: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None


class FeishuCard(BaseModel):
    """飞书消息卡片模型"""
    elements: List[Dict[str, Any]]


class FeishuCardMessage(BaseModel):
    """飞书卡片消息模型"""
    msg_type: str = "interactive"
    card: FeishuCard
    timestamp: Optional[str] = None
    sign: Optional[str] = None


class APIResponse(BaseModel):
    """API响应模型"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthCheck(BaseModel):
    """健康检查模型"""
    status: str = "healthy"
    service: str = "feishu-github-bot"
    version: str = "1.0.0"
    endpoints: Dict[str, str] = Field(default_factory=lambda: {
        "health": "/health",
        "test": "/test", 
        "webhook": "/github-webhook",
        "docs": "/docs"
    }) 