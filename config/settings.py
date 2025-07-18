#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置文件
"""

import os
from typing import Dict, List

# 基础配置
BASE_CONFIG = {
    'project_name': '微信公众号招聘信息监控系统',
    'version': '1.0.0',
    'description': '自动监控微信公众号招聘信息，使用OCR识别图片文字，AI分析内容，生成结构化报告',
    'author': 'AI Assistant',
    'created': '2024-01-01'
}

# 监控配置
MONITOR_CONFIG = {
    'check_interval': 30,  # 检查间隔(分钟)
    'max_articles_per_check': 50,  # 每次检查最大文章数
    'image_download_timeout': 30,  # 图片下载超时时间(秒)
    'api_request_timeout': 30,  # API请求超时时间(秒)
    'max_retries': 3,  # 最大重试次数
    'retry_delay': 5,  # 重试延迟(秒)
}

# OCR配置
OCR_CONFIG = {
    'use_gpu': False,  # 是否使用GPU
    'language': 'ch',  # 语言设置
    'max_image_size': 2048,  # 最大图片尺寸
    'confidence_threshold': 0.5,  # 置信度阈值
    'preprocess_images': True,  # 是否预处理图片
}

# AI分析配置
AI_CONFIG = {
    'model_name': 'deepseek-chat',
    'max_tokens': 2000,
    'temperature': 0.3,
    'api_base_url': 'https://api.deepseek.com',
    'request_delay': 1,  # 请求间隔(秒)
}

# 通知配置
NOTIFICATION_CONFIG = {
    'email_enabled': True,
    'wechat_enabled': True,
    'server_chan_enabled': True,
    'notification_threshold': 1,  # 最少招聘信息数量才发送通知
    'include_attachments': True,  # 是否包含附件
    'max_jobs_in_summary': 5,  # 摘要中最多显示的招聘信息数量
}

# 文件配置
FILE_CONFIG = {
    'data_dir': 'data',
    'logs_dir': 'logs',
    'images_dir': 'data/images',
    'reports_dir': 'data/reports',
    'cache_dir': 'data/cache',
    'max_log_files': 10,  # 最大日志文件数
    'max_image_files': 1000,  # 最大图片文件数
    'log_retention_days': 7,  # 日志保留天数
    'image_retention_days': 3,  # 图片保留天数
}

# 招聘关键词配置
JOB_KEYWORDS = {
    'general': [
        '招聘', '求职', '职位', '岗位', '工作', '面试', '简历', '人才',
        '应聘', '录用', '入职', '试用', '转正', '晋升'
    ],
    'salary': [
        '薪资', '工资', '薪水', '待遇', '福利', '五险一金', '年薪', '月薪',
        '奖金', '提成', '补贴', '津贴', '保险', '公积金'
    ],
    'employment_type': [
        '全职', '兼职', '实习', '临时', '合同', '正式', '试用期',
        '远程', '居家', '驻场', '出差', '外派'
    ],
    'film_industry': [
        '副导演', '导演', '制片', '摄影', '剪辑', '后期', '编导',
        '影视', '传媒', '广告', '制作', '策划', '文案', '运营',
        '摄像', '录音', '灯光', '美术', '化妆', '服装', '道具',
        '场记', '统筹', '制片人', '监制', '编剧', '配音', '特效'
    ],
    'skills': [
        '经验', '学历', '专业', '技能', '能力', '熟练', '精通',
        '本科', '专科', '硕士', '年以上', '相关经验'
    ],
    'contact': [
        '联系', '电话', '微信', '邮箱', '地址', '简历发送',
        '有意者', '请联系', '咨询', '报名'
    ]
}

# 环境变量映射
ENV_VARS = {
    'deepseek_api_key': 'DEEPSEEK_API_KEY',
    'smtp_server': 'SMTP_SERVER',
    'smtp_port': 'SMTP_PORT',
    'sender_email': 'SENDER_EMAIL',
    'sender_password': 'SENDER_PASSWORD',
    'sender_name': 'SENDER_NAME',
    'receiver_emails': 'RECEIVER_EMAILS',
    'wechat_webhook_url': 'WECHAT_WEBHOOK_URL',
    'wechat_mentioned_list': 'WECHAT_MENTIONED_LIST',
    'server_chan_key': 'SERVER_CHAN_KEY',
    'github_token': 'GITHUB_TOKEN'
}

# 获取环境变量
def get_env_config() -> Dict:
    """获取环境变量配置"""
    config = {}
    for key, env_var in ENV_VARS.items():
        value = os.getenv(env_var)
        if value:
            config[key] = value
    return config

# 获取完整配置
def get_config() -> Dict:
    """获取完整配置"""
    config = {
        'base': BASE_CONFIG,
        'monitor': MONITOR_CONFIG,
        'ocr': OCR_CONFIG,
        'ai': AI_CONFIG,
        'notification': NOTIFICATION_CONFIG,
        'file': FILE_CONFIG,
        'keywords': JOB_KEYWORDS,
        'env': get_env_config()
    }
    return config

# 验证配置
def validate_config() -> List[str]:
    """验证配置完整性"""
    errors = []
    env_config = get_env_config()
    
    # 检查必需的环境变量
    required_vars = ['deepseek_api_key']
    for var in required_vars:
        if var not in env_config:
            errors.append(f"缺少必需的环境变量: {ENV_VARS[var]}")
    
    # 检查通知配置
    if NOTIFICATION_CONFIG['email_enabled']:
        email_vars = ['smtp_server', 'sender_email', 'sender_password', 'receiver_emails']
        for var in email_vars:
            if var not in env_config:
                errors.append(f"邮件通知需要环境变量: {ENV_VARS[var]}")
    
    if NOTIFICATION_CONFIG['wechat_enabled']:
        if 'wechat_webhook_url' not in env_config:
            errors.append(f"企业微信通知需要环境变量: {ENV_VARS['wechat_webhook_url']}")
    
    if NOTIFICATION_CONFIG['server_chan_enabled']:
        if 'server_chan_key' not in env_config:
            errors.append(f"Server酱通知需要环境变量: {ENV_VARS['server_chan_key']}")
    
    return errors

# 打印配置信息
def print_config():
    """打印配置信息"""
    config = get_config()
    print("=" * 50)
    print(f"项目: {config['base']['project_name']}")
    print(f"版本: {config['base']['version']}")
    print(f"描述: {config['base']['description']}")
    print("=" * 50)
    
    print("监控配置:")
    for key, value in config['monitor'].items():
        print(f"  {key}: {value}")
    
    print("\nOCR配置:")
    for key, value in config['ocr'].items():
        print(f"  {key}: {value}")
    
    print("\nAI配置:")
    for key, value in config['ai'].items():
        if key != 'api_key':  # 不显示敏感信息
            print(f"  {key}: {value}")
    
    print("\n通知配置:")
    for key, value in config['notification'].items():
        print(f"  {key}: {value}")
    
    print("\n环境变量:")
    env_config = config['env']
    for key in ENV_VARS:
        status = "✓" if key in env_config else "✗"
        print(f"  {key}: {status}")
    
    # 验证配置
    errors = validate_config()
    if errors:
        print("\n配置错误:")
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print("\n✓ 配置验证通过")
    
    print("=" * 50)

if __name__ == "__main__":
    print_config()