"""
常量配置文件
存储飞书机器人的配置信息
"""

# 飞书机器人配置
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/8bfe55f6-afce-418d-a8ac-3346262417e6"
FEISHU_SECRET = "hwYaNNh81lJVs7RUdqVMZd"

# GitHub配置（可选，用于验证webhook请求的安全性）
# 这个密钥需要与GitHub仓库Webhook设置中的Secret保持一致
# 如果不需要验证，可以留空
GITHUB_SECRET = "mluQWsgP1KmICAjHERKJPNkaJj_cJ2DIfgbfNs7H7lQ"  # 与GitHub Webhook设置保持一致

# 服务配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
LOG_LEVEL = "INFO" 