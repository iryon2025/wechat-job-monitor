# GitHub部署指南

## 🚀 快速部署到GitHub Actions

### 1. 创建GitHub仓库

1. 登录GitHub，创建新的仓库
2. 将本项目所有文件上传到仓库

### 2. 配置GitHub Secrets

在仓库的 **Settings > Secrets and variables > Actions** 中添加以下secrets：

#### 必需配置
- `DEEPSEEK_API_KEY`: `sk-92d52c5e40fc48bd89bbe1fd60ebb45e` (已配置)

#### 可选配置 (邮件通知)
- `SMTP_SERVER`: `smtp.gmail.com` (Gmail) 或 `smtp.qq.com` (QQ邮箱)
- `SMTP_PORT`: `587`
- `SENDER_EMAIL`: 您的邮箱地址
- `SENDER_PASSWORD`: 邮箱应用密码
- `SENDER_NAME`: `招聘信息监控系统`
- `RECEIVER_EMAILS`: 接收邮件的地址 (多个用逗号分隔)

#### 可选配置 (企业微信通知)
- `WECHAT_WEBHOOK_URL`: 企业微信机器人webhook地址
- `WECHAT_MENTIONED_LIST`: @的用户列表

#### 可选配置 (Server酱通知)
- `SERVER_CHAN_KEY`: Server酱的SCKEY

### 3. 启用GitHub Actions

1. 进入仓库的 **Actions** 标签页
2. 如果看到禁用提示，点击启用
3. 系统会自动每30分钟运行一次
4. 也可以手动点击 **Run workflow** 立即运行

### 4. 监控运行状态

- 在Actions页面查看运行状态
- 每次运行都会生成报告文件
- 如果配置了通知，会自动发送到指定渠道

## 📊 当前配置状态

### RSS源配置
- ✅ **校影**: 已配置
- ✅ **深焦DeepFocus**: 已配置
- ✅ **备用RSS源**: 已准备

### API配置
- ✅ **DeepSeek API**: 已配置密钥
- ⚠️ **邮件通知**: 需要配置邮箱信息
- ⚠️ **企业微信**: 需要配置webhook
- ⚠️ **Server酱**: 需要配置密钥

## 🔧 本地测试

在上传到GitHub之前，您可以本地测试：

```bash
# 运行快速启动脚本
python start_monitor.py

# 或者运行测试脚本
python test_system.py
```

## 📧 邮件配置指南

### Gmail配置
1. 开启两步验证
2. 生成应用密码
3. 使用应用密码而非账户密码

### QQ邮箱配置
1. 开启SMTP服务
2. 获取授权码
3. 使用授权码作为密码

### 163邮箱配置
1. 开启SMTP服务
2. 设置客户端授权密码
3. 使用授权密码

## 🎯 预期效果

配置完成后，系统将：

1. **每30分钟自动检查** 校影和深焦DeepFocus的新文章
2. **智能识别招聘信息** 使用AI分析文章内容
3. **提取图片文字** 自动识别招聘图片中的文字
4. **生成详细报告** Excel、CSV、JSON三种格式
5. **多渠道通知** 发送到邮箱、微信等

## 💰 费用说明

- **GitHub Actions**: 免费 (2000分钟/月)
- **DeepSeek API**: 约1-5元/月
- **总费用**: 极低成本运行

## 🔍 故障排除

如果遇到问题：

1. 检查Actions运行日志
2. 确认RSS源地址是否正确
3. 验证API密钥是否有效
4. 检查网络连接

## 📞 获取RSS源

如果默认的RSS源不可用，可以尝试：

1. **RSSHub**: https://rsshub.app/wechat/mp/articles/[公众号ID]
2. **Wechat2RSS**: https://wechat2rss.xlab.app/rss/[公众号ID]
3. **今天看啥**: https://www.jintiankansha.me/

需要找到校影和深焦DeepFocus的具体公众号ID。