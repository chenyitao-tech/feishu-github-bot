from typing import Dict, Any, Literal
from pydantic import BaseModel, HttpUrl, Field, field_validator, ConfigDict


class GitHubPRInfo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    
    repo_name: str = Field(..., description="仓库名称")
    pr_title: str = Field(..., description="PR标题")
    pr_number: int = Field(..., gt=0, description="PR号码，必须大于0")
    author_name: str = Field(..., description="操作者名称")
    action: Literal["opened", "closed", "reopened", "synchronize"] = Field(..., description="PR操作类型")
    is_merged: bool = Field(default=False, description="是否已合并")
    source_branch: str = Field(..., description="源分支")
    target_branch: str = Field(..., description="目标分支")
    pr_url: HttpUrl = Field(..., description="PR链接")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """验证 action 字段的有效性"""
        valid_actions = ["opened", "closed", "reopened", "synchronize"]
        if v not in valid_actions:
            raise ValueError(f"action 必须是以下值之一: {valid_actions}")
        return v
    
    @field_validator('is_merged')
    @classmethod
    def validate_merged_status(cls, v: bool, info) -> bool:
        """验证合并状态的逻辑性"""
        if 'action' in info.data and info.data['action'] == 'opened' and v is True:
            raise ValueError("新创建的PR不能是已合并状态")
        return v

    def get_content(self) -> str:
        return f"• **仓库**: {self.repo_name}\n• **PR标题**: {self.pr_title}\n• **PR号**: #{self.pr_number}\n• **操作者**: {self.author_name}\n• **源分支**: {self.source_branch}\n• **目标分支**: {self.target_branch}"

    def create_feishu_card(self) -> Dict[str, Any]:
        if self.action == "opened":
            icon = "🔄"
            title = "Pull Request 创建"
            template = "green"
        elif self.action == "closed" and self.is_merged:
            icon = "✅"
            title = "Pull Request 已合并"
            template = "blue"
        elif self.action == "closed" and not self.is_merged:
            icon = "❌"
            title = "Pull Request 已关闭"
            template = "red"
        else:
            icon = "🔄"
            title = "Pull Request 更新"
            template = "blue"

        content = f"{icon} **{title}**\n\n{self.get_content()}"

        return {
            "msg_type": "interactive",
            "card": {
                "elements": [
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
                                "text": {"content": "查看 PR", "tag": "lark_md"},
                                "url": str(self.pr_url),  # HttpUrl需要转换为字符串
                                "type": "default",
                                "value": {},
                            }
                        ],
                        "tag": "action",
                    },
                ],
                "header": {
                    "title": {"content": title, "tag": "plain_text"},
                    "template": template,
                },
            },
        }
