from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class PRAction(str, Enum):
    """PR 操作类型枚举"""
    OPENED = "opened"
    CLOSED = "closed"
    REOPENED = "reopened"
    SYNCHRONIZE = "synchronize"


class CardStyle(BaseModel):
    """卡片样式配置"""
    model_config = ConfigDict(frozen=True)
    
    icon: str = Field(..., description="图标")
    title: str = Field(..., description="标题")
    template: str = Field(..., description="卡片模板")


class PushCardStyle(BaseModel):
    """推送卡片样式配置"""
    model_config = ConfigDict(frozen=True)
    
    icon: str = Field(default="🚀", description="图标")
    title: str = Field(default="GitHub 推送通知", description="标题")
    template: str = Field(default="blue", description="卡片模板")