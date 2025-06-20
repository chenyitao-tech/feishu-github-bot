from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GitHubPRInfo:
    repo_name: str
    pr_title: str
    pr_number: int
    author_name: str
    action: str  # opened, closed
    is_merged: bool
    source_branch: str
    target_branch: str
    pr_url: str

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
                                "url": self.pr_url,
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
