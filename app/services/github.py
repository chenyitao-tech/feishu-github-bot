"""
GitHub服务模块
处理GitHub webhook验证和数据处理
"""
import hmac
import hashlib
from typing import Optional
import logging

from app.config import settings 

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self):
        self.secret = settings.github_secret
    
    def verify_signature(self, payload_body: bytes, signature_header: Optional[str]) -> bool:
        """验证GitHub webhook签名"""
        if not self.secret:
            # 如果没有配置密钥，跳过验证
            logger.warning("GitHub webhook密钥未配置，跳过签名验证")
            return True
        if not signature_header:
            logger.error("缺少GitHub签名头")
            return False
        try:
            hash_object = hmac.new(
                self.secret.encode('utf-8'), 
                payload_body, 
                hashlib.sha256
            )
            expected_signature = "sha256=" + hash_object.hexdigest()
            # 使用constant time comparison防止时序攻击
            is_valid = hmac.compare_digest(expected_signature, signature_header)
            if is_valid:
                logger.info("GitHub webhook签名验证成功")
            else:
                logger.error("GitHub webhook签名验证失败")
            return is_valid
        except Exception as e:
            logger.error(f"GitHub webhook签名验证异常: {e}")
            return False
    
    def is_push_event(self, event_type: Optional[str]) -> bool:
        """检查是否为推送事件"""
        return event_type == 'push'
    
    def should_ignore_push(self, payload: dict) -> bool:
        """判断是否应该忽略此推送"""
        # 忽略删除分支的推送
        if payload.get('deleted'):
            logger.info("忽略删除分支的推送")
            return True
        # 忽略没有提交的推送
        commits = payload.get('commits', [])
        if not commits:
            logger.info("忽略没有提交的推送")
            return True
        # 可以在这里添加更多过滤条件
        # 例如：忽略特定分支、特定用户等
        return False


# 全局GitHub服务实例
github_service = GitHubService() 