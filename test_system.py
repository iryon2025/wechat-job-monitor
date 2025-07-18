#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于测试各个模块的功能
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rss_monitor import RSSMonitor
from ocr_processor import OCRProcessor
from content_analyzer import ContentAnalyzer
from job_extractor import JobExtractor
from notification import NotificationSender
from config.settings import get_config, validate_config, print_config

def test_config():
    """测试配置"""
    print("=" * 50)
    print("测试配置模块")
    print("=" * 50)
    
    try:
        print_config()
        
        errors = validate_config()
        if errors:
            print("\n配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("\n✓ 配置验证通过")
            return True
            
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False

def test_rss_monitor():
    """测试RSS监控模块"""
    print("=" * 50)
    print("测试RSS监控模块")
    print("=" * 50)
    
    try:
        monitor = RSSMonitor()
        print("✓ RSS监控器初始化成功")
        
        # 测试配置加载
        sources = monitor.load_rss_sources()
        print(f"✓ RSS源配置加载成功: {len(sources)} 个源")
        
        # 测试时间处理
        last_check = monitor.get_last_check_time()
        print(f"✓ 上次检查时间: {last_check}")
        
        return True
        
    except Exception as e:
        print(f"✗ RSS监控测试失败: {e}")
        return False

def test_ocr_processor():
    """测试OCR处理器"""
    print("=" * 50)
    print("测试OCR处理器")
    print("=" * 50)
    
    try:
        processor = OCRProcessor()
        print("✓ OCR处理器初始化成功")
        
        if processor.is_available():
            print("✓ PaddleOCR可用")
            
            # 测试关键词过滤
            test_text = "招聘副导演一名，薪资8000-12000元/月，联系电话13800138000"
            result = processor.filter_job_related_text(test_text)
            print(f"✓ 关键词过滤测试: 发现{len(result['job_keywords'])}个关键词")
            
        else:
            print("⚠ PaddleOCR不可用，将跳过OCR功能")
            
        return True
        
    except Exception as e:
        print(f"✗ OCR处理器测试失败: {e}")
        return False

def test_content_analyzer():
    """测试内容分析器"""
    print("=" * 50)
    print("测试内容分析器")
    print("=" * 50)
    
    try:
        analyzer = ContentAnalyzer()
        print("✓ 内容分析器初始化成功")
        
        if analyzer.is_available():
            print("✓ DeepSeek API可用")
        else:
            print("⚠ DeepSeek API不可用，请检查API密钥")
            
        return True
        
    except Exception as e:
        print(f"✗ 内容分析器测试失败: {e}")
        return False

def test_job_extractor():
    """测试招聘信息提取器"""
    print("=" * 50)
    print("测试招聘信息提取器")
    print("=" * 50)
    
    try:
        extractor = JobExtractor()
        print("✓ 招聘信息提取器初始化成功")
        
        # 测试薪资解析
        test_salary = "8000-12000元/月"
        salary_info = extractor.extract_salary_range(test_salary)
        print(f"✓ 薪资解析测试: {salary_info['min_salary']}-{salary_info['max_salary']} {salary_info['currency']}")
        
        # 测试联系信息提取
        test_contact = {
            'phone': '13800138000',
            'email': 'test@example.com',
            'wechat': 'test_wechat'
        }
        contact_info = extractor.extract_contact_info(test_contact)
        print(f"✓ 联系信息提取测试: 电话{contact_info['phone']}, 邮箱{contact_info['email']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 招聘信息提取器测试失败: {e}")
        return False

def test_notification():
    """测试通知模块"""
    print("=" * 50)
    print("测试通知模块")
    print("=" * 50)
    
    try:
        sender = NotificationSender()
        print("✓ 通知发送器初始化成功")
        
        # 测试邮件内容生成
        test_summary = {
            'statistics': {
                'total_articles': 5,
                'job_related_articles': 3,
                'confirmed_job_postings': 2
            }
        }
        
        test_jobs = [
            {
                'job_title': '副导演',
                'company_name': '测试影视公司',
                'location': '北京',
                'salary_min': 8000,
                'salary_max': 12000,
                'contact_phone': '13800138000'
            }
        ]
        
        subject, text_content, html_content = sender.generate_email_content(test_summary, test_jobs)
        print(f"✓ 邮件内容生成测试: 主题长度{len(subject)}, 内容长度{len(text_content)}")
        
        # 测试微信内容生成
        wechat_content = sender.generate_wechat_content(test_summary, test_jobs)
        print(f"✓ 微信内容生成测试: 内容长度{len(wechat_content)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 通知模块测试失败: {e}")
        return False

def test_main_workflow():
    """测试主工作流程"""
    print("=" * 50)
    print("测试主工作流程")
    print("=" * 50)
    
    try:
        # 创建测试文章数据
        test_articles = [
            {
                'title': '急招副导演',
                'source': '测试公众号',
                'published': datetime.now().isoformat(),
                'link': 'https://test.com/1',
                'full_content': '招聘副导演一名，要求有相关经验，薪资8000-12000元/月，联系电话13800138000',
                'images': [],
                'is_job_related': True,
                'has_job_images': False,
                'job_extraction': {
                    'success': True,
                    'job_info': {
                        'is_job_posting': True,
                        'company_name': '测试影视公司',
                        'positions': [
                            {
                                'job_title': '副导演',
                                'location': '北京',
                                'salary': '8000-12000元/月',
                                'requirements': ['有相关经验', '熟悉影视制作流程']
                            }
                        ],
                        'contact_info': {
                            'phone': '13800138000',
                            'email': 'test@test.com'
                        }
                    }
                }
            }
        ]
        
        # 测试信息提取
        extractor = JobExtractor()
        jobs = extractor.extract_all_jobs(test_articles)
        print(f"✓ 招聘信息提取: {len(jobs)} 个职位")
        
        if jobs:
            # 测试报告生成
            result = extractor.process_articles_and_generate_reports(test_articles)
            print(f"✓ 报告生成: {result['success']}, 文件数量: {len(result.get('files', {}))}")
            
            # 测试通知
            sender = NotificationSender()
            summary = {
                'statistics': {
                    'total_articles': len(test_articles),
                    'job_related_articles': 1,
                    'confirmed_job_postings': 1
                }
            }
            
            subject, _, _ = sender.generate_email_content(summary, jobs)
            print(f"✓ 通知内容生成: {subject}")
        
        return True
        
    except Exception as e:
        print(f"✗ 主工作流程测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始系统测试...")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    tests = [
        ("配置模块", test_config),
        ("RSS监控模块", test_rss_monitor),
        ("OCR处理器", test_ocr_processor),
        ("内容分析器", test_content_analyzer),
        ("招聘信息提取器", test_job_extractor),
        ("通知模块", test_notification),
        ("主工作流程", test_main_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print()
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
            print()
    
    # 汇总结果
    print("=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 个通过, {failed} 个失败")
    print(f"成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！系统已就绪。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查配置。")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)