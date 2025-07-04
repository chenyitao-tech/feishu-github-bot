import re
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from feishu_bot.models import PushCardStyle


class GitHubPushInfo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    repo_name: str = Field(..., description="仓库名称")
    branch_name: str = Field(..., description="分支名称")
    author_name: str = Field(..., description="提交者名称")
    commit_sha: str = Field(..., min_length=7, max_length=40, description="提交SHA值")
    commit_message: str = Field(..., max_length=500, description="提交信息，最长500字符")
    commit_url: HttpUrl = Field(..., description="提交链接")

    @field_validator("commit_sha")
    @classmethod
    def validate_commit_sha(cls, v: str) -> str:
        """验证提交SHA格式"""
        if not re.match(r"^[a-f0-9]{7,40}$", v):
            raise ValueError("commit_sha 必须是7-40位的十六进制字符串")
        return v

    @field_validator("branch_name")
    @classmethod
    def validate_branch_name(cls, v: str) -> str:
        """验证分支名称格式"""
        if not v or v.strip() == "":
            raise ValueError("分支名称不能为空")
        # 检查是否包含非法字符
        illegal_chars = [" ", "~", "^", ":", "?", "*", "["]
        if any(char in v for char in illegal_chars):
            raise ValueError("分支名称包含非法字符")
        return v.strip()

    @field_validator("commit_message")
    @classmethod
    def validate_commit_message(cls, v: str) -> str:
        """验证提交信息"""
        if not v or v.strip() == "":
            raise ValueError("提交信息不能为空")
        return v.strip()

    @property
    def card_style(self) -> PushCardStyle:
        """获取卡片样式配置"""
        return PushCardStyle()

    def get_content(self) -> str:
        """获取卡片内容"""
        style = self.card_style
        fields = [
            f"{style.icon} **代码推送通知**",
            "",
            f"• **仓库**: {self.repo_name}",
            f"• **分支**: {self.branch_name}",
            f"• **提交者**: {self.author_name}",
            f"• **提交ID**: `{self.commit_sha}`",
            f"• **提交信息**: {self.commit_message}",
        ]
        return "\n".join(fields)

    def _create_card_elements(self, content: str) -> list[Dict[str, Any]]:
        """创建卡片元素"""
        return [
            {
                "tag": "div",
                "text": {
                    "content": content,
                    "tag": "lark_md",
                },
            },
            {
                "actions": [
                    {
                        "tag": "button",
                        "text": {"content": "查看提交", "tag": "lark_md"},
                        "url": str(self.commit_url),
                        "type": "default",
                        "value": {},
                    }
                ],
                "tag": "action",
            },
        ]

    def create_feishu_card(self) -> Dict[str, Any]:
        """创建飞书卡片消息"""
        style = self.card_style
        content = self.get_content()

        return {
            "msg_type": "interactive",
            "card": {
                "elements": self._create_card_elements(content),
                "header": {
                    "title": {"content": style.title, "tag": "plain_text"},
                    "template": style.template,
                },
            },
        }
