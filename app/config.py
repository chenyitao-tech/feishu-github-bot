import os
from typing import Optional
from . import constants


class Settings:
    def __init__(self):
        # 飞书机器人配置 - 优先使用环境变量，否则使用constants中的配置
        self.feishu_webhook_url: str = os.getenv('FEISHU_WEBHOOK_URL', constants.FEISHU_WEBHOOK_URL)
        self.feishu_secret: Optional[str] = os.getenv('FEISHU_SECRET', constants.FEISHU_SECRET)
        
        # GitHub配置
        self.github_secret: Optional[str] = os.getenv('GITHUB_SECRET', constants.GITHUB_SECRET)
        
        # 服务配置
        self.host: str = os.getenv('HOST', constants.HOST)
        self.port: int = int(os.getenv('PORT', str(constants.PORT)))
        self.debug: bool = os.getenv('DEBUG', str(constants.DEBUG)).lower() == 'true'
        
        # 日志配置
        self.log_level: str = os.getenv('LOG_LEVEL', constants.LOG_LEVEL)
    
    def validate(self) -> bool:
        """验证必要配置是否存在"""
        if not self.feishu_webhook_url:
            print("❌ 错误: FEISHU_WEBHOOK_URL 环境变量未设置")
            return False
        return True
    
    def display_config(self):
        """显示当前配置"""
        print("=" * 60)
        print("🤖 飞书GitHub机器人配置")
        print("=" * 60)
        print(f"飞书Webhook: {self.feishu_webhook_url[:50]}..." if self.feishu_webhook_url else "飞书Webhook: ❌ 未配置")
        print(f"飞书签名: {'✅ 已配置' if self.feishu_secret else '⚠️ 未配置'}")
        print(f"GitHub签名: {'✅ 已配置' if self.github_secret else '⚠️ 未配置'}")
        print(f"服务地址: http://{self.host}:{self.port}")
        print(f"调试模式: {'✅ 开启' if self.debug else '❌ 关闭'}")
        print("=" * 60)
        print("📡 可用接口:")
        print(f"  - 首页: http://localhost:{self.port}/")
        print(f"  - 测试: http://localhost:{self.port}/test")
        print(f"  - Webhook: http://localhost:{self.port}/github-webhook")
        print(f"  - API文档: http://localhost:{self.port}/docs")
        print("=" * 60)


settings = Settings() 