from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GitHubPushInfo:
    repo_name: str
    branch_name: str
    author_name: str
    commit_sha: str
    commit_message: str
    commit_url: str

    def get_content(self) -> str:
        return f"🚀 **代码推送通知**\n\n• **仓库**: {self.repo_name}\n• **分支**: {self.branch_name}\n• **提交者**: {self.author_name}\n• **提交ID**: `{self.commit_sha}`\n• **提交信息**: {self.commit_message}"

    def create_feishu_card(self) -> Dict[str, Any]:
        return {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": self.get_content(),
                            "tag": "lark_md",
                        },
                    },
                    {
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"content": "查看提交", "tag": "lark_md"},
                                "url": self.commit_url,
                                "type": "default",
                                "value": {},
                            }
                        ],
                        "tag": "action",
                    },
                ],
                "header": {
                    "title": {"content": "GitHub 推送通知", "tag": "plain_text"},
                    "template": "blue",
                },
            },
        }
