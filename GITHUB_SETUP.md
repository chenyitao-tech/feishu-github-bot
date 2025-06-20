# GitHub配置指南

## 🚀 将项目推送到GitHub

### 1. 创建GitHub仓库

1. 登录GitHub，点击右上角的 `+` → `New repository`
2. 填写仓库信息：
   - **Repository name**: `feishu-github-bot`
   - **Description**: `飞书GitHub机器人 - 将GitHub推送事件通知到飞书群`
   - **Public/Private**: 选择Public（开源）或Private（私有）
   - 不要初始化README、.gitignore或license（因为我们已经有了）

### 2. 推送代码到GitHub

```bash
# 初始化git仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "feat: 初始化飞书GitHub机器人项目"

# 添加远程仓库（替换为你的GitHub用户名和仓库名）
git remote add origin https://github.com/你的用户名/feishu-github-bot.git

# 推送到GitHub
git push -u origin main
```

## 🔗 配置GitHub Webhook

### 1. 部署服务器

首先你需要将机器人部署到公网可访问的服务器：

#### 选项A: 使用云服务器
- **阿里云ECS**、**腾讯云CVM**、**AWS EC2**等
- 确保开放8000端口
- 获取公网IP地址

#### 选项B: 使用内网穿透（开发测试）
```bash
# 使用ngrok（需要先安装）
ngrok http 8000

# 会得到类似这样的公网地址：
# https://abc123.ngrok.io
```

#### 选项C: 使用免费部署平台
- **Railway**: https://railway.app/
- **Render**: https://render.com/
- **Heroku**: https://heroku.com/

### 2. 在GitHub仓库中配置Webhook

1. **进入仓库设置**：
   ```
   你的仓库 → Settings → Webhooks → Add webhook
   ```

2. **填写Webhook配置**：
   - **Payload URL**: `http://你的服务器IP:8000/github-webhook`
     - 例如：`http://123.456.789.0:8000/github-webhook`
     - 或者：`https://your-app.railway.app/github-webhook`
   
   - **Content type**: 选择 `application/json`
   
   - **Secret**: 输入自定义密钥
     - 例如：`my-github-webhook-secret-2024`
     - 这个密钥需要与 `app/constants.py` 中的 `GITHUB_SECRET` 保持一致
   
   - **Which events would you like to trigger this webhook?**
     - 选择 `Just the push event`
   
   - **Active**: 确保勾选

3. **点击 `Add webhook`**

### 3. 更新项目配置

在 `app/constants.py` 中设置相同的密钥：

```python
# GitHub配置
GITHUB_SECRET = "my-github-webhook-secret-2024"  # 与GitHub Webhook设置保持一致
```

## 🧪 测试配置

### 1. 启动服务
```bash
python main.py
```

### 2. 测试Webhook
推送一个测试提交到仓库：
```bash
echo "# 测试提交" >> test.txt
git add test.txt
git commit -m "test: 测试GitHub webhook"
git push
```

### 3. 检查结果
- 查看飞书群是否收到推送通知
- 查看服务器日志是否有相关记录

## 🔒 安全最佳实践

### 1. 使用强密钥
```python
# ❌ 弱密钥
GITHUB_SECRET = "123456"

# ✅ 强密钥
GITHUB_SECRET = "gh_webhook_2024_secure_key_abc123!@#"
```

### 2. 使用环境变量（生产环境推荐）
```bash
# 设置环境变量
export GITHUB_SECRET="你的强密钥"
export FEISHU_SECRET="你的飞书密钥"
export FEISHU_WEBHOOK_URL="你的飞书webhook地址"

# 然后启动服务
python main.py
```

### 3. 不要将密钥提交到代码仓库
在 `.gitignore` 中添加：
```
# 敏感配置文件
app/constants_prod.py
.env
```

## 🚀 部署示例

### 使用Railway部署

1. **连接GitHub仓库**：
   - 访问 https://railway.app/
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择你的 `feishu-github-bot` 仓库

2. **设置环境变量**：
   ```
   FEISHU_WEBHOOK_URL = https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook
   FEISHU_SECRET = 你的飞书密钥
   GITHUB_SECRET = 你的GitHub密钥
   PORT = 8000
   ```

3. **获取部署地址**：
   - Railway会自动生成一个公网地址
   - 例如：`https://feishu-github-bot-production.up.railway.app`

4. **更新GitHub Webhook URL**：
   ```
   https://feishu-github-bot-production.up.railway.app/github-webhook
   ```

## 📝 常见问题

### Q: GitHub密钥是必须的吗？
A: 不是必须的，但强烈推荐使用。没有密钥的话，任何人都可以向你的webhook发送伪造请求。

### Q: 如何生成安全的密钥？
A: 可以使用以下方式生成：
```bash
# 方式1: 使用openssl
openssl rand -hex 32

# 方式2: 使用Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Q: 本地开发如何测试？
A: 使用ngrok等内网穿透工具：
```bash
# 安装ngrok后
ngrok http 8000

# 使用生成的公网地址配置GitHub Webhook
```

### Q: 服务器重启后webhook失效？
A: 检查：
1. 服务是否正常启动
2. 端口是否开放
3. 防火墙设置
4. 服务器公网IP是否变化 