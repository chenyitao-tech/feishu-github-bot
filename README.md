# 飞书 GitHub 机器人

## 功能特性

- **代码推送通知**：自动发送代码推送信息到飞书群
- **Pull Request 通知**：支持 PR 创建、合并、关闭等状态通知

## 📁 项目结构

```
feishu-robot/
├── .github/
│   └── workflows/
│       └── feishu_notification.yml    # GitHub Actions 工作流配置
├── scripts/
│   └── feishu_notify.py              # 飞书通知脚本
├── feishu_bot/
│   ├── __init__.py                   
│   ├── constants.py                  # 常量定义
│   ├── github_push.py                # 推送通知数据模型
│   └── github_pr.py                  # PR 通知数据模型
├── .gitignore                       
└── README.md                         
```

## 流程

### 1. 获取飞书 Webhook URL

1. 在飞书群聊中添加机器人
2. 获取 Webhook URL（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx`）
3. 设置安全密钥

### 2. 配置 GitHub Secrets

在 GitHub 仓库中设置以下 Secrets：

- `FEISHU_WEBHOOK_URL`：飞书机器人的 Webhook URL
- `FEISHU_SECRET`：飞书机器人的安全密钥

