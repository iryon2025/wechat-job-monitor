#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号招聘信息自动监控系统
主程序入口
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rss_monitor import RSSMonitor
from ocr_processor import OCRProcessor
from content_analyzer import ContentAnalyzer
from job_extractor import JobExtractor
from notification import NotificationSender

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"monitor_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """主函数"""
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("微信公众号招聘信息监控系统启动")
    logger.info("=" * 50)
    
    try:
        # 初始化各个组件
        logger.info("正在初始化系统组件...")
        
        rss_monitor = RSSMonitor()
        ocr_processor = OCRProcessor()
        content_analyzer = ContentAnalyzer()
        job_extractor = JobExtractor()
        notification_sender = NotificationSender()
        
        # 检查组件状态
        logger.info("检查组件状态...")
        
        if not ocr_processor.is_available():
            logger.warning("OCR处理器不可用，将跳过图片文字识别")
        
        if not content_analyzer.is_available():
            logger.warning("内容分析器不可用，将跳过AI分析")
        
        # 步骤1: 监控RSS源，获取新文章
        logger.info("步骤1: 监控RSS源...")
        new_articles = rss_monitor.monitor_rss_sources()
        
        if not new_articles:
            logger.info("没有发现新文章，程序结束")
            return
        
        logger.info(f"发现 {len(new_articles)} 篇新文章")
        
        # 步骤2: 处理文章图片，进行OCR识别
        logger.info("步骤2: 处理文章图片...")
        
        if ocr_processor.is_available():
            processed_articles = []
            for article in new_articles:
                try:
                    processed_article = ocr_processor.process_article_images(article)
                    processed_articles.append(processed_article)
                except Exception as e:
                    logger.error(f"处理文章图片失败: {e}")
                    processed_articles.append(article)
            
            new_articles = processed_articles
            logger.info("图片处理完成")
        else:
            logger.warning("跳过图片处理")
        
        # 步骤3: 使用AI分析文章内容
        logger.info("步骤3: 分析文章内容...")
        
        if content_analyzer.is_available():
            analyzed_articles = content_analyzer.process_articles(new_articles)
            new_articles = analyzed_articles
            logger.info("内容分析完成")
        else:
            logger.warning("跳过内容分析")
        
        # 步骤4: 提取招聘信息并生成报告
        logger.info("步骤4: 提取招聘信息...")
        
        report_result = job_extractor.process_articles_and_generate_reports(new_articles)
        
        if report_result['success']:
            logger.info(f"成功提取 {report_result['job_count']} 个招聘信息")
            logger.info(f"生成的报告文件: {list(report_result['files'].keys())}")
        else:
            logger.warning(f"报告生成失败: {report_result['message']}")
        
        # 步骤5: 发送通知
        logger.info("步骤5: 发送通知...")
        
        # 准备汇总信息
        summary = {
            'statistics': {
                'total_articles': len(new_articles),
                'job_related_articles': len([a for a in new_articles if a.get('is_job_related', False)]),
                'confirmed_job_postings': len([a for a in new_articles if a.get('is_confirmed_job_posting', False)]),
                'articles_with_job_images': len([a for a in new_articles if a.get('has_job_images', False)]),
                'total_positions': report_result.get('job_count', 0)
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # 提取招聘信息用于通知
        jobs = job_extractor.extract_all_jobs(new_articles)
        
        # 准备附件
        attachments = []
        if report_result.get('files'):
            for file_type, file_path in report_result['files'].items():
                if os.path.exists(file_path):
                    attachments.append(file_path)
        
        # 发送通知
        notification_result = notification_sender.send_all_notifications(
            summary, jobs, attachments
        )
        
        if notification_result['success']:
            logger.info(f"通知发送成功: {notification_result['success_count']}/{notification_result['total']}")
        else:
            logger.warning("所有通知发送失败")
        
        # 保存运行结果
        result_file = os.path.join("data", f"run_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        run_result = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'articles_count': len(new_articles),
            'jobs_count': len(jobs),
            'report_files': report_result.get('files', {}),
            'notification_result': notification_result,
            'success': True
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(run_result, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 50)
        logger.info("监控任务完成")
        logger.info(f"新文章: {len(new_articles)} 篇")
        logger.info(f"招聘信息: {len(jobs)} 个")
        logger.info(f"报告文件: {len(report_result.get('files', {}))} 个")
        logger.info(f"通知发送: {notification_result['success_count']}/{notification_result['total']}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"系统运行出错: {e}", exc_info=True)
        
        # 保存错误结果
        error_file = os.path.join("data", f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        error_result = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'success': False
        }
        
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()