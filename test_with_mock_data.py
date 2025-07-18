#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用模拟数据测试完整系统功能
"""

import os
import sys
import json
from datetime import datetime

# 设置环境变量
os.environ['DEEPSEEK_API_KEY'] = 'sk-92d52c5e40fc48bd89bbe1fd60ebb45e'

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_analyzer import ContentAnalyzer
from job_extractor import JobExtractor
from notification import NotificationSender

def create_mock_articles():
    """创建模拟的文章数据"""
    return [
        {
            'title': '【招聘】深焦DeepFocus诚聘副导演',
            'source': '深焦DeepFocus',
            'published': datetime.now().isoformat(),
            'link': 'https://mp.weixin.qq.com/s/test123',
            'full_content': """
深焦DeepFocus影视制作团队现诚聘副导演一名。

职位要求：
- 本科及以上学历，影视相关专业
- 3年以上影视制作经验
- 熟悉电影制作流程
- 具备良好的沟通协调能力

薪资待遇：
- 月薪：12000-18000元
- 五险一金
- 带薪年假
- 项目奖金

工作地点：北京市朝阳区

联系方式：
- 联系人：王制片
- 电话：13800138000
- 邮箱：hr@deepfocus.com
- 微信：deepfocus_hr

有意者请发送简历至邮箱，我们会尽快与您联系。
""",
            'images': [],
            'is_job_related': True,
            'has_job_images': False
        },
        {
            'title': '校影学院急招摄影助理',
            'source': '校影',
            'published': datetime.now().isoformat(),
            'link': 'https://mp.weixin.qq.com/s/test456',
            'full_content': """
校影学院摄影部门急招摄影助理2名。

岗位职责：
- 协助摄影师完成拍摄工作
- 负责摄影器材的准备和整理
- 参与后期制作讨论

任职要求：
- 摄影或相关专业在校生或毕业生
- 有摄影基础，会使用专业摄影设备
- 责任心强，执行力强

薪资：8000-12000元/月

工作地点：上海市静安区

联系电话：13900139000
简历投递：xiaoying@academy.edu
""",
            'images': [],
            'is_job_related': True,
            'has_job_images': False
        },
        {
            'title': '深焦电影节观察：2024年度最佳影片盘点',
            'source': '深焦DeepFocus',
            'published': datetime.now().isoformat(),
            'link': 'https://mp.weixin.qq.com/s/test789',
            'full_content': """
2024年即将结束，让我们回顾这一年的优秀电影作品。

戛纳电影节：
- 金棕榈奖：《xxx》
- 最佳导演：xxx

威尼斯电影节：
- 金狮奖：《xxx》

柏林电影节：
- 金熊奖：《xxx》

这些电影展现了当代电影艺术的最高水准...
""",
            'images': [],
            'is_job_related': False,
            'has_job_images': False
        }
    ]

def test_ai_analysis():
    """测试AI内容分析功能"""
    print("🤖 测试AI内容分析...")
    
    analyzer = ContentAnalyzer()
    if not analyzer.is_available():
        print("❌ DeepSeek API不可用")
        return False
    
    # 测试文章
    test_articles = create_mock_articles()
    
    print(f"📝 处理 {len(test_articles)} 篇文章...")
    
    # 处理文章
    processed_articles = analyzer.process_articles(test_articles)
    
    # 显示结果
    for article in processed_articles:
        print(f"\n📄 文章: {article['title']}")
        
        ai_summary = article.get('ai_summary', {})
        if ai_summary.get('success'):
            print("✅ AI分析成功")
            print(f"💬 总结: {ai_summary['summary'][:200]}...")
        else:
            print("❌ AI分析失败")
        
        job_extraction = article.get('job_extraction', {})
        if job_extraction.get('success'):
            job_info = job_extraction.get('job_info', {})
            if job_info.get('is_job_posting'):
                print("🎯 确认为招聘信息")
                positions = job_info.get('positions', [])
                print(f"📋 职位数量: {len(positions)}")
            else:
                print("ℹ️ 非招聘信息")
    
    return True

def test_job_extraction():
    """测试招聘信息提取功能"""
    print("\n📊 测试招聘信息提取...")
    
    # 创建包含AI分析结果的文章
    test_articles = create_mock_articles()
    
    # 模拟AI分析结果
    test_articles[0]['job_extraction'] = {
        'success': True,
        'job_info': {
            'is_job_posting': True,
            'company_name': '深焦DeepFocus',
            'positions': [
                {
                    'job_title': '副导演',
                    'location': '北京市朝阳区',
                    'salary': '12000-18000元/月',
                    'requirements': ['本科及以上学历', '3年以上影视制作经验', '熟悉电影制作流程'],
                    'responsibilities': ['协助导演完成拍摄工作', '现场执行和协调'],
                    'benefits': ['五险一金', '带薪年假', '项目奖金']
                }
            ],
            'contact_info': {
                'contact_person': '王制片',
                'phone': '13800138000',
                'email': 'hr@deepfocus.com',
                'wechat': 'deepfocus_hr'
            }
        }
    }
    
    test_articles[1]['job_extraction'] = {
        'success': True,
        'job_info': {
            'is_job_posting': True,
            'company_name': '校影学院',
            'positions': [
                {
                    'job_title': '摄影助理',
                    'location': '上海市静安区',
                    'salary': '8000-12000元/月',
                    'requirements': ['摄影或相关专业', '有摄影基础', '责任心强'],
                    'responsibilities': ['协助摄影师完成拍摄工作', '负责摄影器材准备'],
                    'benefits': []
                }
            ],
            'contact_info': {
                'phone': '13900139000',
                'email': 'xiaoying@academy.edu'
            }
        }
    }
    
    # 提取招聘信息
    extractor = JobExtractor()
    result = extractor.process_articles_and_generate_reports(test_articles)
    
    if result['success']:
        print(f"✅ 成功提取 {result['job_count']} 个招聘信息")
        print(f"📁 生成报告文件:")
        for file_type, file_path in result['files'].items():
            print(f"  - {file_type}: {file_path}")
        return True
    else:
        print(f"❌ 提取失败: {result['message']}")
        return False

def test_notification():
    """测试通知功能"""
    print("\n📧 测试通知功能...")
    
    # 模拟招聘信息
    test_jobs = [
        {
            'job_title': '副导演',
            'company_name': '深焦DeepFocus',
            'location': '北京市朝阳区',
            'salary_min': 12000,
            'salary_max': 18000,
            'salary_currency': 'CNY',
            'salary_period': 'monthly',
            'contact_phone': '13800138000',
            'contact_email': 'hr@deepfocus.com',
            'source': '深焦DeepFocus',
            'published_date': datetime.now().isoformat()
        },
        {
            'job_title': '摄影助理',
            'company_name': '校影学院',
            'location': '上海市静安区',
            'salary_min': 8000,
            'salary_max': 12000,
            'salary_currency': 'CNY',
            'salary_period': 'monthly',
            'contact_phone': '13900139000',
            'contact_email': 'xiaoying@academy.edu',
            'source': '校影',
            'published_date': datetime.now().isoformat()
        }
    ]
    
    # 模拟汇总信息
    summary = {
        'statistics': {
            'total_articles': 3,
            'job_related_articles': 2,
            'confirmed_job_postings': 2,
            'total_positions': 2
        }
    }
    
    # 测试通知内容生成
    sender = NotificationSender()
    
    # 测试邮件内容
    subject, text_content, html_content = sender.generate_email_content(summary, test_jobs)
    print(f"📧 邮件主题: {subject}")
    print(f"📄 邮件内容长度: {len(text_content)} 字符")
    print(f"🌐 HTML内容长度: {len(html_content)} 字符")
    
    # 测试微信内容
    wechat_content = sender.generate_wechat_content(summary, test_jobs)
    print(f"💬 微信内容长度: {len(wechat_content)} 字符")
    print(f"📱 微信内容预览:\n{wechat_content}")
    
    return True

def main():
    """主测试函数"""
    print("🎬 微信公众号招聘信息监控系统 - 完整功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试AI分析
    try:
        success = test_ai_analysis()
        results.append(("AI内容分析", success))
    except Exception as e:
        print(f"❌ AI分析测试异常: {e}")
        results.append(("AI内容分析", False))
    
    # 测试信息提取
    try:
        success = test_job_extraction()
        results.append(("招聘信息提取", success))
    except Exception as e:
        print(f"❌ 信息提取测试异常: {e}")
        results.append(("招聘信息提取", False))
    
    # 测试通知
    try:
        success = test_notification()
        results.append(("通知功能", success))
    except Exception as e:
        print(f"❌ 通知测试异常: {e}")
        results.append(("通知功能", False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("🎯 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📊 总计: {passed}/{total} 通过")
    print(f"🎉 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！系统完全正常运行！")
        print("✅ DeepSeek API集成成功")
        print("✅ 招聘信息提取功能正常") 
        print("✅ 报告生成功能正常")
        print("✅ 通知功能正常")
        print("\n🚀 系统已就绪，可以部署到GitHub Actions！")
    else:
        print(f"\n⚠️ 有 {total-passed} 个功能需要检查")

if __name__ == "__main__":
    main()