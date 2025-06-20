import os
import hmac
import hashlib
import base64
import time
import requests
import subprocess
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GitHubPushInfo:
    """GitHub推送信息"""
    repo_name: str
    branch_name: str
    author_name: str
    commit_sha: str
    commit_message: str
    commit_url: str

    def create_feishu_card(self) -> Dict[str, Any]:
        """创建飞书推送通知卡片"""
        return {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": f"🚀 **代码推送通知**\n\n• **仓库**: {self.repo_name}\n• **分支**: {self.branch_name}\n• **提交者**: {self.author_name}\n• **提交ID**: `{self.commit_sha}`\n• **提交信息**: {self.commit_message}",
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


def get_commit_info() -> tuple[str, str]:
    """获取提交信息"""
    try:
        commit_sha = os.environ.get("GITHUB_SHA", "")[:7]  # 获取提交ID（前7位）
        # 获取提交信息
        result = subprocess.run(
            ["git", "log", "--format=%B", "-n", "1", os.environ.get("GITHUB_SHA", "")],
            capture_output=True,
            text=True,
        )
        commit_message = result.stdout.strip().split("\n")[0] if result.stdout else ""
        return commit_sha, commit_message
    except Exception as e:
        print(f"获取提交信息失败: {e}")
        return "", ""


def generate_signature(timestamp: str, secret: str) -> str | None:
    """生成飞书签名"""
    if not secret:
        return None
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")





def send_feishu_message(webhook_url: str, message: dict, secret: str | None = None) -> bool:
    """发送飞书消息"""
    timestamp = str(int(time.time()))
    # 如果有密钥，添加签名
    if secret:
        sign = generate_signature(timestamp, secret)
        message["timestamp"] = timestamp
        message["sign"] = sign
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("✅ 飞书消息发送成功")
                return True
            else:
                print(f"❌ 飞书消息发送失败: {result}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return False


def main():
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ 未配置 FEISHU_WEBHOOK_URL，跳过飞书通知")
        return

    secret = os.environ.get("FEISHU_SECRET")
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    print(f"📡 处理GitHub事件: {event_name}")
    message = None

    # 处理推送事件
    if event_name == "push":
        commit_sha, commit_message = get_commit_info()
        # 创建推送信息对象
        push_info = GitHubPushInfo(
            repo_name=os.environ.get("GITHUB_REPOSITORY", ""),
            branch_name=os.environ.get("GITHUB_REF_NAME", ""),
            author_name=os.environ.get("GITHUB_ACTOR", ""),
            commit_sha=commit_sha,
            commit_message=commit_message,
            commit_url=f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/commit/{os.environ.get('GITHUB_SHA', '')}"
        )
        # 生成飞书卡片消息
        message = push_info.create_feishu_card()
    else:
        print(f"忽略的事件类型: {event_name}")
        return

    if message:
        success = send_feishu_message(webhook_url, message, secret)
        if not success:
            sys.exit(1)
    else:
        print("❌ 无法创建消息")
        sys.exit(1)


if __name__ == "__main__":
    main()
