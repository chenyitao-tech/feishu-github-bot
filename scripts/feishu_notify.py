import os
import hmac
import hashlib
import base64
import time
import requests
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from feishu_bot.github_push import GitHubPushInfo
from feishu_bot.github_pr import GitHubPRInfo


def get_commit_info() -> tuple[str, str]:
    """获取提交信息"""
    try:
        commit_sha = os.environ.get("GITHUB_SHA", "")[:7]
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


def gen_feishu_signature(timestamp: str, secret: str) -> str | None:
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
        sign = gen_feishu_signature(timestamp, secret)
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
    
    # 处理 Pull Request 事件
    elif event_name == "pull_request":
        action = os.environ.get("GITHUB_EVENT_ACTION", "")
        pr_merged = os.environ.get("PR_MERGED", "false").lower() == "true"
        
        # 创建 PR 信息对象
        pr_info = GitHubPRInfo(
            repo_name=os.environ.get("GITHUB_REPOSITORY", ""),
            pr_title=os.environ.get("PR_TITLE", ""),
            pr_number=int(os.environ.get("PR_NUMBER", "0")),
            author_name=os.environ.get("GITHUB_ACTOR", ""),
            action=action,
            is_merged=pr_merged,
            source_branch=os.environ.get("GITHUB_HEAD_REF", ""),
            target_branch=os.environ.get("GITHUB_BASE_REF", ""),
            pr_url=os.environ.get("PR_URL", "")
        )
        # 生成飞书卡片消息
        message = pr_info.create_feishu_card()
    
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
