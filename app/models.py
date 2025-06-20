from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """健康检查模型"""
    status: str = "healthy"
    message: str = "Service is running"


class APIResponse(BaseModel):
    """API响应模型"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


# 飞书消息相关模型
class FeishuText(BaseModel):
    """飞书文本内容"""
    content: str
    tag: str = "lark_md"


class FeishuButton(BaseModel):
    """飞书按钮"""
    tag: str = "button"
    text: FeishuText
    url: str
    type: str = "default"
    value: Dict[str, Any] = {}


class FeishuAction(BaseModel):
    """飞书动作组件"""
    tag: str = "action"
    actions: List[FeishuButton]


class FeishuDiv(BaseModel):
    """飞书div元素"""
    tag: str = "div"
    text: FeishuText


class FeishuHeader(BaseModel):
    """飞书卡片头部"""
    title: FeishuText
    template: str = "blue"


class FeishuCard(BaseModel):
    """飞书卡片"""
    elements: List[Dict[str, Any]]
    header: FeishuHeader


class FeishuCardMessage(BaseModel):
    """飞书卡片消息"""
    msg_type: str = "interactive"
    card: FeishuCard
    timestamp: Optional[str] = None
    sign: Optional[str] = None

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """自定义序列化方法"""
        return super().model_dump(exclude_none=True, **kwargs)


# GitHub 推送通知专用模型
class GitHubPushInfo(BaseModel):
    """GitHub推送信息"""
    repo_name: str
    branch_name: str
    author_name: str
    commit_sha: str
    commit_message: str
    commit_url: str

    @classmethod
    def create_feishu_card(cls, push_info: 'GitHubPushInfo') -> FeishuCardMessage:
        """创建飞书推送通知卡片"""
        # 创建文本内容
        content_text = FeishuText(
            content=f"🚀 **代码推送通知**\n\n• **仓库**: {push_info.repo_name}\n• **分支**: {push_info.branch_name}\n• **提交者**: {push_info.author_name}\n• **提交ID**: `{push_info.commit_sha}`\n• **提交信息**: {push_info.commit_message}"
        )
        # 创建div元素
        div_element = FeishuDiv(text=content_text)
        # 创建按钮
        view_button = FeishuButton(
            text=FeishuText(content="查看提交"),
            url=push_info.commit_url
        )
        # 创建动作组件
        action_element = FeishuAction(actions=[view_button])
        # 创建头部
        header = FeishuHeader(
            title=FeishuText(content="GitHub 推送通知", tag="plain_text")
        )
        # 创建卡片
        card = FeishuCard(
            elements=[
                div_element.model_dump(),
                action_element.model_dump()
            ],
            header=header
        )
        # 创建完整消息
        return FeishuCardMessage(card=card)
