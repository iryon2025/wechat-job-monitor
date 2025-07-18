#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知推送模块
支持邮件和企业微信等多种通知方式
"""

import smtplib
import logging
import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationSender:
    """通知发送器，支持多种通知方式"""
    
    def __init__(self):
        """初始化通知发送器"""
        self.email_config = self._load_email_config()
        self.wechat_config = self._load_wechat_config()
    
    def _load_email_config(self) -> Dict:
        """加载邮件配置"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', ''),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'sender_name': os.getenv('SENDER_NAME', '招聘信息监控系统'),
            'receiver_emails': os.getenv('RECEIVER_EMAILS', '').split(',') if os.getenv('RECEIVER_EMAILS') else []
        }
    
    def _load_wechat_config(self) -> Dict:
        """加载企业微信配置"""
        return {
            'webhook_url': os.getenv('WECHAT_WEBHOOK_URL', ''),
            'mentioned_list': os.getenv('WECHAT_MENTIONED_LIST', '').split(',') if os.getenv('WECHAT_MENTIONED_LIST') else []
        }
    
    def generate_email_content(self, summary: Dict, jobs: List[Dict]) -> tuple:
        """
        生成邮件内容
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            
        Returns:
            (subject, text_content, html_content)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job_count = len(jobs)
        
        # 邮件主题
        if job_count > 0:
            subject = f"🎬 发现 {job_count} 个新的影视招聘信息 - {timestamp}"
        else:
            subject = f"📄 招聘信息监控报告 - {timestamp}"
        
        # 文本内容
        text_content = f"""
招聘信息监控报告
生成时间: {timestamp}

📊 统计信息:
- 总文章数: {summary.get('statistics', {}).get('total_articles', 0)}
- 招聘相关文章: {summary.get('statistics', {}).get('job_related_articles', 0)}
- 确认的招聘信息: {summary.get('statistics', {}).get('confirmed_job_postings', 0)}
- 提取的职位数: {job_count}

"""
        
        # HTML内容
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>招聘信息监控报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; }}
        .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .job-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .job-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
        .company {{ font-size: 16px; color: #e74c3c; }}
        .location {{ color: #27ae60; }}
        .salary {{ color: #f39c12; font-weight: bold; }}
        .contact {{ background-color: #ecf0f1; padding: 10px; border-radius: 3px; }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 招聘信息监控报告</h1>
        <p>生成时间: {timestamp}</p>
    </div>
    
    <div class="stats">
        <h2>📊 统计信息</h2>
        <ul>
            <li>总文章数: {summary.get('statistics', {}).get('total_articles', 0)}</li>
            <li>招聘相关文章: {summary.get('statistics', {}).get('job_related_articles', 0)}</li>
            <li>确认的招聘信息: {summary.get('statistics', {}).get('confirmed_job_postings', 0)}</li>
            <li>提取的职位数: {job_count}</li>
        </ul>
    </div>
"""
        
        if jobs:
            html_content += "<h2>🔍 招聘信息详情</h2>"
            
            for i, job in enumerate(jobs, 1):
                salary_text = ""
                if job.get('salary_min') and job.get('salary_max'):
                    salary_text = f"{job['salary_min']}-{job['salary_max']} {job.get('salary_currency', 'CNY')}/{job.get('salary_period', 'month')}"
                elif job.get('salary_original'):
                    salary_text = job['salary_original']
                
                contact_parts = []
                if job.get('contact_person'):
                    contact_parts.append(f"联系人: {job['contact_person']}")
                if job.get('contact_phone'):
                    contact_parts.append(f"电话: {job['contact_phone']}")
                if job.get('contact_email'):
                    contact_parts.append(f"邮箱: {job['contact_email']}")
                if job.get('contact_wechat'):
                    contact_parts.append(f"微信: {job['contact_wechat']}")
                
                contact_text = " | ".join(contact_parts) if contact_parts else "暂无联系方式"
                
                html_content += f"""
                <div class="job-item">
                    <div class="job-title">{i}. {job.get('job_title', '未知职位')}</div>
                    <div class="company">🏢 {job.get('company_name', '未知公司')}</div>
                    <div class="location">📍 {job.get('location', '未知地点')}</div>
                    {f'<div class="salary">💰 {salary_text}</div>' if salary_text else ''}
                    
                    {f'<p><strong>任职要求:</strong> {job.get("requirements", "")}</p>' if job.get("requirements") else ''}
                    {f'<p><strong>工作职责:</strong> {job.get("responsibilities", "")}</p>' if job.get("responsibilities") else ''}
                    {f'<p><strong>福利待遇:</strong> {job.get("benefits", "")}</p>' if job.get("benefits") else ''}
                    
                    <div class="contact">
                        <strong>联系方式:</strong> {contact_text}
                    </div>
                    
                    <p><small>来源: {job.get('source', '')} | 发布时间: {job.get('published_date', '')}</small></p>
                </div>
                """
                
                # 添加到文本内容
                text_content += f"""
{i}. {job.get('job_title', '未知职位')}
公司: {job.get('company_name', '未知公司')}
地点: {job.get('location', '未知地点')}
薪资: {salary_text}
联系方式: {contact_text}
来源: {job.get('source', '')}
---
"""
        else:
            html_content += "<p>本次监控未发现新的招聘信息。</p>"
            text_content += "\n本次监控未发现新的招聘信息。\n"
        
        html_content += """
    <div class="footer">
        <p>此邮件由招聘信息监控系统自动生成</p>
        <p>如有疑问，请联系管理员</p>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content
    
    def send_email(self, summary: Dict, jobs: List[Dict], attachments: List[str] = None) -> bool:
        """
        发送邮件通知
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            attachments: 附件文件路径列表
            
        Returns:
            发送是否成功
        """
        if not self.email_config['sender_email'] or not self.email_config['receiver_emails']:
            logger.warning("邮件配置不完整，跳过邮件发送")
            return False
        
        try:
            # 生成邮件内容
            subject, text_content, html_content = self.generate_email_content(summary, jobs)
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.email_config['sender_name'], self.email_config['sender_email']))
            msg['To'] = ', '.join(self.email_config['receiver_emails'])
            
            # 添加文本和HTML内容
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # 发送邮件
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['receiver_emails'], text)
            server.quit()
            
            logger.info(f"邮件发送成功，发送给: {', '.join(self.email_config['receiver_emails'])}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def generate_wechat_content(self, summary: Dict, jobs: List[Dict]) -> str:
        """
        生成企业微信消息内容
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            
        Returns:
            消息内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job_count = len(jobs)
        
        content = f"""🎬 招聘信息监控报告
📅 时间: {timestamp}

📊 统计信息:
• 总文章数: {summary.get('statistics', {}).get('total_articles', 0)}
• 招聘相关: {summary.get('statistics', {}).get('job_related_articles', 0)}
• 确认招聘: {summary.get('statistics', {}).get('confirmed_job_postings', 0)}
• 提取职位: {job_count}

"""
        
        if jobs:
            content += "🔍 招聘信息摘要:\n"
            for i, job in enumerate(jobs[:5], 1):  # 只显示前5个
                salary_text = ""
                if job.get('salary_min') and job.get('salary_max'):
                    salary_text = f" | 💰 {job['salary_min']}-{job['salary_max']}"
                elif job.get('salary_original'):
                    salary_text = f" | 💰 {job['salary_original']}"
                
                content += f"{i}. {job.get('job_title', '未知职位')} @ {job.get('company_name', '未知公司')}{salary_text}\n"
            
            if len(jobs) > 5:
                content += f"... 还有 {len(jobs) - 5} 个职位，详情请查看邮件\n"
        else:
            content += "本次监控未发现新的招聘信息\n"
        
        content += "\n📧 详细信息请查看邮件附件"
        
        return content
    
    def send_wechat_notification(self, summary: Dict, jobs: List[Dict]) -> bool:
        """
        发送企业微信通知
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            
        Returns:
            发送是否成功
        """
        if not self.wechat_config['webhook_url']:
            logger.warning("企业微信配置不完整，跳过微信通知")
            return False
        
        try:
            content = self.generate_wechat_content(summary, jobs)
            
            # 构建消息数据
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            # 如果有@人员列表
            if self.wechat_config['mentioned_list']:
                data["text"]["mentioned_list"] = self.wechat_config['mentioned_list']
            
            # 发送请求
            response = requests.post(
                self.wechat_config['webhook_url'],
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info("企业微信通知发送成功")
                return True
            else:
                logger.error(f"企业微信通知发送失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"企业微信通知发送失败: {e}")
            return False
    
    def send_server_chan_notification(self, summary: Dict, jobs: List[Dict]) -> bool:
        """
        发送Server酱通知
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            
        Returns:
            发送是否成功
        """
        server_chan_key = os.getenv('SERVER_CHAN_KEY', '')
        if not server_chan_key:
            logger.warning("Server酱配置不完整，跳过通知")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            job_count = len(jobs)
            
            if job_count > 0:
                title = f"🎬 发现 {job_count} 个新的影视招聘信息"
            else:
                title = f"📄 招聘信息监控报告"
            
            content = f"""
时间: {timestamp}

统计信息:
- 总文章数: {summary.get('statistics', {}).get('total_articles', 0)}
- 招聘相关: {summary.get('statistics', {}).get('job_related_articles', 0)}
- 确认招聘: {summary.get('statistics', {}).get('confirmed_job_postings', 0)}
- 提取职位: {job_count}

"""
            
            if jobs:
                content += "招聘信息摘要:\n"
                for i, job in enumerate(jobs[:3], 1):  # 只显示前3个
                    content += f"{i}. {job.get('job_title', '未知职位')} @ {job.get('company_name', '未知公司')}\n"
            
            # 发送到Server酱
            url = f"https://sctapi.ftqq.com/{server_chan_key}.send"
            data = {
                'title': title,
                'desp': content
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                logger.info("Server酱通知发送成功")
                return True
            else:
                logger.error(f"Server酱通知发送失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Server酱通知发送失败: {e}")
            return False
    
    def send_all_notifications(self, summary: Dict, jobs: List[Dict], attachments: List[str] = None) -> Dict:
        """
        发送所有配置的通知
        
        Args:
            summary: 汇总信息
            jobs: 招聘信息列表
            attachments: 附件文件路径列表
            
        Returns:
            发送结果
        """
        results = {}
        
        # 发送邮件
        if self.email_config['sender_email']:
            results['email'] = self.send_email(summary, jobs, attachments)
        
        # 发送企业微信
        if self.wechat_config['webhook_url']:
            results['wechat'] = self.send_wechat_notification(summary, jobs)
        
        # 发送Server酱
        server_chan_key = os.getenv('SERVER_CHAN_KEY', '')
        if server_chan_key:
            results['server_chan'] = self.send_server_chan_notification(summary, jobs)
        
        # 统计发送结果
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"通知发送完成: {success_count}/{total_count} 成功")
        
        return {
            'success': success_count > 0,
            'total': total_count,
            'success_count': success_count,
            'results': results
        }


def test_notification():
    """测试通知功能"""
    sender = NotificationSender()
    
    # 测试数据
    test_summary = {
        'statistics': {
            'total_articles': 5,
            'job_related_articles': 3,
            'confirmed_job_postings': 2,
            'total_positions': 2
        }
    }
    
    test_jobs = [
        {
            'job_title': '副导演',
            'company_name': '测试影视公司',
            'location': '北京',
            'salary_min': 8000,
            'salary_max': 12000,
            'salary_currency': 'CNY',
            'salary_period': 'monthly',
            'contact_phone': '13800138000',
            'source': '测试公众号',
            'published_date': '2024-01-01'
        }
    ]
    
    # 测试发送通知
    results = sender.send_all_notifications(test_summary, test_jobs)
    print(f"测试结果: {results}")


if __name__ == "__main__":
    test_notification()