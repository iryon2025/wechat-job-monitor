# 微信公众号招聘信息自动监控系统

🎬 一个智能化的微信公众号招聘信息监控系统，专为影视行业招聘信息收集设计，支持自动监控、OCR识别、AI分析和多渠道通知。

## ✨ 主要特性

- 🔍 **自动监控**: 通过RSS源监控微信公众号文章更新
- 🖼️ **图片识别**: 使用PaddleOCR识别招聘图片中的文字信息
- 🤖 **AI分析**: 集成DeepSeek API进行内容智能分析和总结
- 📊 **结构化提取**: 自动提取招聘信息并生成Excel/CSV报告
- 📧 **多渠道通知**: 支持邮件、企业微信、Server酱等通知方式
- ☁️ **云端运行**: 基于GitHub Actions，24小时自动运行
- 💰 **成本极低**: 月成本仅1-5元，主要为DeepSeek API费用

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RSS 监控      │ -> │   OCR 图片识别   │ -> │   AI 内容分析   │
│ (Wechat2RSS)    │    │ (PaddleOCR 3.0) │    │ (DeepSeek API)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           v                       v                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   信息提取      │ -> │   报告生成      │ -> │   通知推送      │
│ (结构化数据)    │    │ (Excel/CSV)     │    │ (邮件/微信)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 安装与配置

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd wechat_job_monitor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置RSS源

编辑 `config/rss_sources.json` 文件，添加您要监控的公众号RSS源：

```json
[
  {
    "name": "影视招聘公众号",
    "url": "https://rsshub.app/wechat/mp/articles/你的公众号ID",
    "description": "影视行业招聘信息",
    "enabled": true
  }
]
```

### 4. 环境变量配置

创建 `.env` 文件或设置环境变量：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=招聘监控系统
RECEIVER_EMAILS=receiver1@gmail.com,receiver2@gmail.com

# 企业微信配置
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
WECHAT_MENTIONED_LIST=@all

# Server酱配置
SERVER_CHAN_KEY=your_server_chan_key
```

## 🚀 使用方法

### 本地运行

```bash
python main.py
```

### GitHub Actions 自动运行

1. **Fork 项目到您的GitHub仓库**

2. **配置GitHub Secrets**

   在仓库的 Settings > Secrets and variables > Actions 中添加以下secrets：

   - `DEEPSEEK_API_KEY`: DeepSeek API密钥
   - `SMTP_SERVER`: SMTP服务器地址
   - `SMTP_PORT`: SMTP端口
   - `SENDER_EMAIL`: 发送者邮箱
   - `SENDER_PASSWORD`: 邮箱密码
   - `SENDER_NAME`: 发送者名称
   - `RECEIVER_EMAILS`: 接收者邮箱(逗号分隔)
   - `WECHAT_WEBHOOK_URL`: 企业微信机器人webhook
   - `SERVER_CHAN_KEY`: Server酱密钥

3. **启用Actions**

   Actions会每30分钟自动运行，也可以手动触发

## 📊 输出报告

系统会自动生成多种格式的报告：

- **Excel报告**: 包含详细的招聘信息表格和统计数据
- **CSV报告**: 便于数据分析和导入其他系统
- **JSON报告**: 原始数据格式，便于程序处理

### 报告字段说明

| 字段 | 说明 |
|------|------|
| `company_name` | 公司名称 |
| `job_title` | 职位名称 |
| `location` | 工作地点 |
| `salary_min/max` | 薪资范围 |
| `requirements` | 任职要求 |
| `contact_phone` | 联系电话 |
| `contact_email` | 联系邮箱 |
| `published_date` | 发布时间 |
| `source` | 来源公众号 |

## 🔧 高级配置

### OCR配置

```python
OCR_CONFIG = {
    'use_gpu': False,          # 是否使用GPU加速
    'language': 'ch',          # 语言设置
    'confidence_threshold': 0.5 # 置信度阈值
}
```

### AI分析配置

```python
AI_CONFIG = {
    'model_name': 'deepseek-chat',
    'max_tokens': 2000,
    'temperature': 0.3
}
```

### 通知配置

```python
NOTIFICATION_CONFIG = {
    'notification_threshold': 1,    # 最少招聘信息数量才发送通知
    'max_jobs_in_summary': 5,      # 摘要中最多显示的招聘信息数量
    'include_attachments': True     # 是否包含附件
}
```

## 📈 成本分析

| 服务 | 费用 | 说明 |
|------|------|------|
| GitHub Actions | 免费 | 每月2000分钟免费额度 |
| PaddleOCR | 免费 | 开源OCR解决方案 |
| DeepSeek API | 1-5元/月 | 按使用量计费 |
| 邮件服务 | 免费 | 使用Gmail等免费邮箱 |
| **总计** | **1-5元/月** | 极低成本运行 |

## 🛠️ 开发指南

### 项目结构

```
wechat_job_monitor/
├── .github/workflows/          # GitHub Actions配置
├── src/                        # 源代码
│   ├── rss_monitor.py         # RSS监控模块
│   ├── ocr_processor.py       # OCR图片识别
│   ├── content_analyzer.py    # AI内容分析
│   ├── job_extractor.py       # 招聘信息提取
│   └── notification.py        # 通知推送
├── config/                     # 配置文件
├── data/                      # 数据存储
├── logs/                      # 日志文件
├── main.py                    # 主程序
└── requirements.txt           # 依赖包
```

### 添加新的通知方式

1. 在 `src/notification.py` 中添加新的通知方法
2. 在 `config/settings.py` 中添加相应配置
3. 在主程序中调用新的通知方法

### 自定义关键词

编辑 `config/settings.py` 中的 `JOB_KEYWORDS` 配置：

```python
JOB_KEYWORDS = {
    'your_industry': [
        '关键词1', '关键词2', '关键词3'
    ]
}
```

## 🔍 常见问题

### Q: 如何获取微信公众号的RSS源？

A: 可以使用以下服务：
- [RSSHub](https://rsshub.app/)
- [Wechat2RSS](https://github.com/ttttmr/Wechat2RSS)
- [今天看啥](https://www.jintiankansha.me/)

### Q: DeepSeek API如何获取？

A: 访问 [DeepSeek官网](https://www.deepseek.com/) 注册账号并获取API密钥

### Q: 如何设置企业微信机器人？

A: 在企业微信群中添加机器人，获取webhook地址

### Q: 系统支持哪些邮箱服务？

A: 支持所有SMTP协议的邮箱服务，如Gmail、QQ邮箱、163邮箱等

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 🔍 RSS监控功能
- 🖼️ OCR图片识别
- 🤖 AI内容分析
- 📊 报告生成
- 📧 多渠道通知

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [DeepSeek API](https://www.deepseek.com/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [RSSHub](https://rsshub.app/)
- [GitHub Actions](https://github.com/features/actions)

---

💡 如果这个项目对您有帮助，请给个⭐️支持一下！