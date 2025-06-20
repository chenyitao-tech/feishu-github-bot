import hmac
import hashlib
import base64
import requests
from datetime import datetime
from typing import Dict, Any
import logging

from app.config import settings
from app.models import GitHubWebhookPayload

logger = logging.getLogger(__name__)


class FeishuService:
    def __init__(self):
        self.webhook_url = settings.feishu_webhook_url
        self.secret = settings.feishu_secret

    def generate_signature(self, timestamp: str) -> str:
        """生成飞书签名"""
        if not self.secret:
            return ""
        # 拼接timestamp和secret
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return sign

    def send_message(self, message_data: Dict[str, Any]) -> bool:
        """发送消息到飞书"""
        if not self.webhook_url:
            logger.error("飞书webhook地址未配置")
            return False
        timestamp = str(int(datetime.now().timestamp()))
        message_data["timestamp"] = timestamp
        # 如果配置了签名，添加签名
        if self.secret:
            sign = self.generate_signature(timestamp)
            message_data["sign"] = sign
        try:
            response = requests.post(
                self.webhook_url,
                json=message_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info("飞书消息发送成功")
                    return True
                else:
                    logger.error(f"飞书消息发送失败: {result}")
                    return False
            else:
                logger.error(f"飞书消息发送失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"发送飞书消息异常: {e}")
            return False

    def send_text_message(self, text: str) -> bool:
        """发送文本消息"""
        message_data = {"msg_type": "text", "content": {"text": text}}
        return self.send_message(message_data)

    def send_card_message(self, card: Dict[str, Any]) -> bool:
        """发送卡片消息"""
        message_data = {"msg_type": "interactive", "card": card}
        return self.send_message(message_data)

    def create_push_card(self, payload: GitHubWebhookPayload) -> Dict[str, Any]:
        """创建推送通知卡片"""
        repo_name = payload.repository.full_name
        pusher_name = payload.pusher.name
        commits = payload.commits
        branch = payload.ref.replace("refs/heads/", "")

        # 构建提交信息
        commit_elements = []
        for commit in commits[:3]:  # 最多显示3个提交
            commit_message = commit.message.split("\n")[0][:50]
            if len(commit.message) > 50:
                commit_message += "..."
            commit_elements.append(
                {
                    "tag": "div",
                    "text": {"content": f"• {commit_message}", "tag": "plain_text"},
                }
            )
        if len(commits) > 3:
            commit_elements.append(
                {
                    "tag": "div",
                    "text": {
                        "content": f"... 还有 {len(commits) - 3} 个提交",
                        "tag": "plain_text",
                    },
                }
            )
        # 构建卡片
        card_elements = [
            {
                "tag": "div",
                "text": {
                    "content": f"**{pusher_name}** 向 **{repo_name}** 推送了代码",
                    "tag": "lark_md",
                },
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {"content": f"**分支:** {branch}", "tag": "lark_md"},
                    },
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**提交数:** {len(commits)}",
                            "tag": "lark_md",
                        },
                    },
                ],
            },
        ]
        # 添加提交信息
        if commit_elements:
            card_elements.append(
                {"tag": "div", "text": {"content": "**提交信息:**", "tag": "lark_md"}}
            )
            card_elements.extend(commit_elements)
        # 添加查看链接
        if payload.repository.html_url:
            card_elements.extend(
                [
                    {"tag": "hr"},
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"content": "查看仓库", "tag": "plain_text"},
                                "url": payload.repository.html_url,
                                "type": "primary",
                            }
                        ],
                    },
                ]
            )
        return {"elements": card_elements}

    def create_test_card(self) -> Dict[str, Any]:
        """创建测试卡片"""
        return {
            "elements": [
                {
                    "tag": "div",
                    "text": {"content": "**测试消息**", "tag": "lark_md"},
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "content": "这是一条测试消息，用于验证飞书机器人配置是否正确。",
                        "tag": "plain_text",
                    },
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**发送时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {"content": "**状态:** 正常", "tag": "lark_md"},
                        },
                    ],
                },
            ]
        }


# 全局飞书服务实例
feishu_service = FeishuService()
