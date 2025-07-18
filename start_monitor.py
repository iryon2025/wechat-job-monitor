#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
使用您的配置快速启动监控系统
"""

import os
import sys

# 设置环境变量
os.environ['DEEPSEEK_API_KEY'] = 'sk-92d52c5e40fc48bd89bbe1fd60ebb45e'

# 如果您有邮件配置，请取消注释并填写
# os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SENDER_EMAIL'] = 'your_email@gmail.com'
# os.environ['SENDER_PASSWORD'] = 'your_app_password'
# os.environ['RECEIVER_EMAILS'] = 'your_email@gmail.com'

print("🎬 微信公众号招聘信息监控系统启动")
print("=" * 50)
print("监控的公众号:")
print("  - 校影")
print("  - 深焦DeepFocus")
print("=" * 50)

# 运行主程序
if __name__ == "__main__":
    from main import main
    main()