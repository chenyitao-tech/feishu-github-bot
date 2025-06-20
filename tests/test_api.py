#!/usr/bin/env python3
"""
FastAPI版本的测试脚本
"""
import json
import requests
import hmac
import hashlib
from typing import Optional

# 测试数据
test_payload = {
    "ref": "refs/heads/main",
    "repository": {
        "full_name": "test-user/test-repo",
        "html_url": "https://github.com/test-user/test-repo"
    },
    "pusher": {
        "name": "test-user"
    },
    "commits": [
        {
            "message": "修复了登录页面的样式问题",
            "url": "https://github.com/test-user/test-repo/commit/abc123"
        },
        {
            "message": "添加了用户头像上传功能\n\n- 支持jpg、png格式\n- 自动压缩图片",
            "url": "https://github.com/test-user/test-repo/commit/def456"
        }
    ]
}


def generate_github_signature(payload: dict, secret: str) -> str:
    """生成GitHub webhook签名"""
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def test_health_check(base_url: str = "http://localhost:8000"):
    """测试健康检查接口"""
    print("🏥 测试健康检查接口...")
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_feishu_message(base_url: str = "http://localhost:8000"):
    """测试飞书消息发送"""
    print("\n📱 测试飞书消息发送...")
    
    try:
        response = requests.get(f"{base_url}/test")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 飞书消息测试失败: {e}")
        return False


def test_github_webhook(base_url: str = "http://localhost:8000", secret: Optional[str] = None):
    """测试GitHub webhook"""
    print("\n🔗 测试GitHub webhook...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'push',
        'User-Agent': 'GitHub-Hookshot/test'
    }
    
    # 如果提供了密钥，添加签名
    if secret:
        signature = generate_github_signature(test_payload, secret)
        headers['X-Hub-Signature-256'] = signature
        print(f"使用签名: {signature}")
    
    try:
        response = requests.post(
            f"{base_url}/github-webhook",
            json=test_payload,
            headers=headers,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ GitHub webhook测试失败: {e}")
        return False


def test_api_docs(base_url: str = "http://localhost:8000"):
    """测试API文档"""
    print("\n📚 测试API文档...")
    
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"API文档状态码: {response.status_code}")
        
        response = requests.get(f"{base_url}/openapi.json")
        print(f"OpenAPI规范状态码: {response.status_code}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False


def main():
    """主测试函数"""
    import sys
    
    base_url = "http://localhost:8000"
    secret = None
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        secret = sys.argv[2]
    
    print("🧪 FastAPI版本测试脚本")
    print("=" * 60)
    print(f"服务地址: {base_url}")
    print(f"使用签名: {'是' if secret else '否'}")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("健康检查", lambda: test_health_check(base_url)),
        ("飞书消息", lambda: test_feishu_message(base_url)),
        ("GitHub Webhook", lambda: test_github_webhook(base_url, secret)),
        ("API文档", lambda: test_api_docs(base_url)),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print("=" * 60)
    print(f"总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查配置和服务状态")


if __name__ == "__main__":
    main() 