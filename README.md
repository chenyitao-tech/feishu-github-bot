# 飞书GitHub机器人 v2.0

这是一个用于将GitHub推送事件通知到飞书群的现代化机器人项目。基于FastAPI构建，具有高性能、类型安全和自动API文档生成等特性。

## ✨ 功能特性

- 🚀 **FastAPI框架** - 现代化、高性能的Web框架
- 📨 **GitHub Webhook** - 实时接收GitHub推送事件
- 💬 **飞书消息** - 发送美观的卡片消息到飞书群
- 🔒 **安全验证** - 支持GitHub和飞书的签名验证
- 📊 **自动文档** - 自动生成OpenAPI文档
- 🧪 **完整测试** - 提供全面的测试工具
- 📦 **模块化设计** - 清晰的项目结构，易于扩展
- 🔍 **类型安全** - 基于Pydantic的数据验证

## 快速开始

### 1. 创建飞书自定义机器人

1. 在飞书群中，点击群设置 → 群机器人 → 添加机器人 → 自定义机器人
2. 填写机器人名称和描述
3. 安全设置选择"签名校验"（推荐）或"自定义关键词"
4. 复制生成的Webhook地址和签名密钥

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置机器人信息

编辑 `app/constants.py` 文件，填入你的飞书机器人配置：

```python
# 飞书机器人配置
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id"
FEISHU_SECRET = "your-feishu-secret"

# GitHub配置（可选）
GITHUB_SECRET = "your-github-webhook-secret"  # 如果需要GitHub签名验证
```

或者使用环境变量（优先级更高）：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id"
export FEISHU_SECRET="your-feishu-secret"
export GITHUB_SECRET="your-github-webhook-secret"
```

### 4. 启动服务

```bash
# 方式1: 直接启动
python main.py

# 方式2: 使用uvicorn启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动。

### 5. 测试飞书消息发送

```bash
# 使用新的测试脚本
python tests/test_api.py

# 或直接访问测试接口
curl http://localhost:8000/test
```

### 6. 查看API文档

FastAPI自动生成的交互式API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 7. 配置GitHub Webhook

1. 进入你的GitHub仓库设置页面
2. 点击 "Webhooks" → "Add webhook"
3. 填写配置：
   - **Payload URL**: `http://your-server.com:8000/github-webhook`
   - **Content type**: `application/json`
   - **Secret**: 填入你设置的 `GITHUB_SECRET`（可选）
   - **Events**: 选择 "Just the push event"
4. 点击 "Add webhook"

## 📁 项目结构

```
feishu-robot/
├── app/                          # 主应用包
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # FastAPI主应用
│   ├── config.py                # 配置管理
│   ├── constants.py             # 常量配置
│   ├── models.py                # 数据模型
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── webhook.py           # Webhook处理
│   │   └── health.py            # 健康检查
│   └── services/                # 业务服务
│       ├── __init__.py
│       ├── feishu.py            # 飞书服务
│       └── github.py            # GitHub服务
├── tests/                       # 测试模块
│   ├── __init__.py
│   └── test_api.py              # API测试
├── main.py                      # 应用入口文件
├── requirements.txt             # 依赖包
└── README.md                    # 说明文档
```

## API接口

### GitHub Webhook接口

- **URL**: `/github-webhook`
- **方法**: `POST`
- **用途**: 接收GitHub推送事件

### 测试接口

- **URL**: `/test`
- **方法**: `GET`
- **用途**: 测试飞书消息发送功能

### 首页

- **URL**: `/`
- **方法**: `GET`
- **用途**: 查看服务状态

## 部署建议

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用Docker部署

创建 `Dockerfile`：
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

构建和运行：
```bash
docker build -t feishu-github-bot .
docker run -d -p 5000:5000 \
  -e FEISHU_WEBHOOK_URL="your-webhook-url" \
  -e FEISHU_SECRET="your-secret" \
  feishu-github-bot
```

### 使用systemd服务

创建 `/etc/systemd/system/feishu-bot.service`：
```ini
[Unit]
Description=Feishu GitHub Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
Environment=FEISHU_WEBHOOK_URL=your-webhook-url
Environment=FEISHU_SECRET=your-secret
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable feishu-bot
sudo systemctl start feishu-bot
```

## 消息格式示例

当你推送代码时，飞书群中会收到类似这样的消息：

```
🚀 张三 向 myorg/myproject 推送了代码

分支: main          提交数: 2

提交信息:
• 修复了登录页面的样式问题
• 添加了用户头像上传功能

[查看仓库]
```

## 常见问题

### 1. 收不到通知？

- 检查飞书机器人配置是否正确
- 检查GitHub Webhook是否配置正确
- 查看服务日志是否有错误信息
- 确保服务器可以从外网访问

### 2. 签名验证失败？

- 确保飞书机器人的签名密钥配置正确
- 确保GitHub Webhook的密钥配置正确
- 检查时间戳是否正确

### 3. 如何自定义消息格式？

修改 `create_push_card()` 函数中的卡片结构，参考飞书消息卡片开发文档。

## 扩展功能

你可以根据需要扩展更多功能：

- 支持更多GitHub事件（Issues、Pull Request等）
- 添加@特定用户功能
- 支持多个飞书群通知
- 添加消息过滤规则
- 集成其他代码托管平台

## 参考文档

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [飞书自定义机器人](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)
- [GitHub Webhooks文档](https://docs.github.com/en/developers/webhooks-and-events/webhooks)

## 许可证

MIT License 