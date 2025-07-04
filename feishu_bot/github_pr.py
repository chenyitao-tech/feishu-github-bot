from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from feishu_bot.models import CardStyle, PRAction


class GitHubPRInfo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    repo_name: str = Field(..., description="仓库名称")
    pr_title: str = Field(..., description="PR标题")
    pr_number: int = Field(..., gt=0, description="PR号码，必须大于0")
    author_name: str = Field(..., description="操作者名称")
    action: PRAction = Field(..., description="PR操作类型")
    is_merged: bool = Field(default=False, description="是否已合并")
    source_branch: str = Field(..., description="源分支")
    target_branch: str = Field(..., description="目标分支")
    pr_url: HttpUrl = Field(..., description="PR链接")

    @field_validator("is_merged")
    @classmethod
    def validate_merged_status(cls, v: bool, info) -> bool:
        """验证合并状态的逻辑性"""
        if "action" in info.data and info.data["action"] == PRAction.OPENED and v is True:
            raise ValueError("新创建的PR不能是已合并状态")
        return v

    @property
    def card_style(self) -> CardStyle:
        """获取卡片样式配置"""
        style_map = {
            PRAction.OPENED: CardStyle(icon="🔄", title="Pull Request 创建", template="green"),
            PRAction.REOPENED: CardStyle(icon="🔄", title="Pull Request 重新打开", template="blue"),
            PRAction.SYNCHRONIZE: CardStyle(icon="🔄", title="Pull Request 更新", template="blue"),
        }

        if self.action == PRAction.CLOSED:
            if self.is_merged:
                return CardStyle(icon="✅", title="Pull Request 已合并", template="blue")
            else:
                return CardStyle(icon="❌", title="Pull Request 已关闭", template="red")

        return style_map.get(self.action, CardStyle(icon="🔄", title="Pull Request 更新", template="blue"))

    def get_content(self) -> str:
        """获取卡片内容"""
        fields = [
            f"• **仓库**: {self.repo_name}",
            f"• **PR标题**: {self.pr_title}",
            f"• **PR号**: #{self.pr_number}",
            f"• **操作者**: {self.author_name}",
            f"• **源分支**: {self.source_branch}",
            f"• **目标分支**: {self.target_branch}",
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
                        "text": {"content": "查看 PR", "tag": "lark_md"},
                        "url": str(self.pr_url),
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
        content = f"{style.icon} **{style.title}**\n\n{self.get_content()}"

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
