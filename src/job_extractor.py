#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘信息结构化提取器
将分析后的招聘信息转换为结构化数据并生成表格
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobExtractor:
    """招聘信息提取器，负责结构化处理和表格生成"""
    
    def __init__(self, output_dir: str = "data"):
        """
        初始化招聘信息提取器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text or text == "未提及":
            return ""
        
        # 去除多余空格和换行
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 去除特殊字符
        text = re.sub(r'[^\w\s\-\.@\(\)（），。、：；！？/]', '', text)
        
        return text
    
    def extract_salary_range(self, salary_text: str) -> Dict:
        """
        提取薪资范围
        
        Args:
            salary_text: 薪资文本
            
        Returns:
            薪资信息字典
        """
        if not salary_text or salary_text == "未提及":
            return {
                'min_salary': None,
                'max_salary': None,
                'currency': 'CNY',
                'period': 'monthly',
                'original_text': salary_text
            }
        
        # 清理文本
        clean_text = self.clean_text(salary_text)
        
        # 提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', clean_text)
        
        # 判断货币单位
        currency = 'CNY'
        if any(unit in clean_text.lower() for unit in ['$', 'usd', 'dollar']):
            currency = 'USD'
        elif any(unit in clean_text.lower() for unit in ['€', 'eur', 'euro']):
            currency = 'EUR'
        
        # 判断时间单位
        period = 'monthly'
        if any(unit in clean_text for unit in ['年', '年薪', 'year', 'annual']):
            period = 'yearly'
        elif any(unit in clean_text for unit in ['日', '天', 'day', 'daily']):
            period = 'daily'
        elif any(unit in clean_text for unit in ['时', '小时', 'hour', 'hourly']):
            period = 'hourly'
        
        # 提取薪资范围
        min_salary = None
        max_salary = None
        
        if len(numbers) >= 2:
            min_salary = float(numbers[0])
            max_salary = float(numbers[1])
        elif len(numbers) == 1:
            # 如果只有一个数字，根据上下文判断
            if any(word in clean_text for word in ['以上', '起', '+']):
                min_salary = float(numbers[0])
            elif any(word in clean_text for word in ['以下', '内', '-']):
                max_salary = float(numbers[0])
            else:
                min_salary = float(numbers[0])
        
        return {
            'min_salary': min_salary,
            'max_salary': max_salary,
            'currency': currency,
            'period': period,
            'original_text': salary_text
        }
    
    def extract_contact_info(self, contact_data: Dict) -> Dict:
        """
        提取联系信息
        
        Args:
            contact_data: 联系信息原始数据
            
        Returns:
            标准化的联系信息
        """
        if not contact_data:
            return {}
        
        # 提取电话号码
        phone_patterns = [
            r'1[3-9]\d{9}',  # 中国手机号
            r'0\d{2,3}-?\d{7,8}',  # 中国座机号
            r'\+86\s?1[3-9]\d{9}'  # 带国家代码的手机号
        ]
        
        phone = contact_data.get('phone', '')
        if phone and phone != "未提及":
            for pattern in phone_patterns:
                match = re.search(pattern, phone)
                if match:
                    phone = match.group(0)
                    break
        
        # 提取邮箱
        email = contact_data.get('email', '')
        if email and email != "未提及":
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
            if email_match:
                email = email_match.group(0)
        
        # 提取微信号
        wechat = contact_data.get('wechat', '')
        if wechat and wechat != "未提及":
            wechat = self.clean_text(wechat)
        
        return {
            'contact_person': self.clean_text(contact_data.get('contact_person', '')),
            'phone': phone if phone != "未提及" else '',
            'email': email if email != "未提及" else '',
            'wechat': wechat if wechat != "未提及" else '',
            'address': self.clean_text(contact_data.get('address', '')),
            'application_method': self.clean_text(contact_data.get('application_method', ''))
        }
    
    def extract_job_from_article(self, article: Dict) -> List[Dict]:
        """
        从文章中提取招聘信息
        
        Args:
            article: 文章数据
            
        Returns:
            招聘信息列表
        """
        jobs = []
        
        try:
            # 获取AI提取的信息
            job_extraction = article.get('job_extraction', {})
            if not job_extraction.get('success'):
                return jobs
            
            job_info = job_extraction.get('job_info', {})
            if not job_info.get('is_job_posting'):
                return jobs
            
            # 基础信息
            company_name = self.clean_text(job_info.get('company_name', ''))
            contact_info = self.extract_contact_info(job_info.get('contact_info', {}))
            deadline = self.clean_text(job_info.get('deadline', ''))
            additional_info = self.clean_text(job_info.get('additional_info', ''))
            
            # 处理职位信息
            positions = job_info.get('positions', [])
            if not positions:
                # 如果没有职位信息，创建一个默认的
                positions = [{'job_title': '未指定职位'}]
            
            for position in positions:
                # 提取薪资信息
                salary_info = self.extract_salary_range(position.get('salary', ''))
                
                # 处理要求和职责
                requirements = position.get('requirements', [])
                if isinstance(requirements, str):
                    requirements = [requirements]
                requirements_text = '; '.join([self.clean_text(req) for req in requirements if req and req != "未提及"])
                
                responsibilities = position.get('responsibilities', [])
                if isinstance(responsibilities, str):
                    responsibilities = [responsibilities]
                responsibilities_text = '; '.join([self.clean_text(resp) for resp in responsibilities if resp and resp != "未提及"])
                
                benefits = position.get('benefits', [])
                if isinstance(benefits, str):
                    benefits = [benefits]
                benefits_text = '; '.join([self.clean_text(ben) for ben in benefits if ben and ben != "未提及"])
                
                # 创建职位记录
                job_record = {
                    # 基础信息
                    'article_title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'published_date': article.get('published', ''),
                    'article_url': article.get('link', ''),
                    'extraction_time': datetime.now().isoformat(),
                    
                    # 公司信息
                    'company_name': company_name,
                    'company_address': contact_info.get('address', ''),
                    
                    # 职位信息
                    'job_title': self.clean_text(position.get('job_title', '')),
                    'department': self.clean_text(position.get('department', '')),
                    'location': self.clean_text(position.get('location', '')),
                    'employment_type': self.clean_text(position.get('employment_type', '')),
                    
                    # 薪资信息
                    'salary_min': salary_info.get('min_salary'),
                    'salary_max': salary_info.get('max_salary'),
                    'salary_currency': salary_info.get('currency', 'CNY'),
                    'salary_period': salary_info.get('period', 'monthly'),
                    'salary_original': salary_info.get('original_text', ''),
                    
                    # 详细信息
                    'requirements': requirements_text,
                    'responsibilities': responsibilities_text,
                    'benefits': benefits_text,
                    
                    # 联系信息
                    'contact_person': contact_info.get('contact_person', ''),
                    'contact_phone': contact_info.get('phone', ''),
                    'contact_email': contact_info.get('email', ''),
                    'contact_wechat': contact_info.get('wechat', ''),
                    'application_method': contact_info.get('application_method', ''),
                    
                    # 其他信息
                    'deadline': deadline,
                    'additional_info': additional_info,
                    
                    # 标记信息
                    'is_confirmed': True,
                    'has_image_text': article.get('has_job_images', False),
                    'ai_confidence': job_extraction.get('usage', {}).get('total_tokens', 0) > 0
                }
                
                jobs.append(job_record)
                
        except Exception as e:
            logger.error(f"从文章中提取招聘信息失败: {e}")
        
        return jobs
    
    def extract_all_jobs(self, articles: List[Dict]) -> List[Dict]:
        """
        从所有文章中提取招聘信息
        
        Args:
            articles: 文章列表
            
        Returns:
            所有招聘信息列表
        """
        all_jobs = []
        
        for article in articles:
            try:
                jobs = self.extract_job_from_article(article)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"处理文章失败: {e}")
                continue
        
        logger.info(f"共提取到 {len(all_jobs)} 个招聘信息")
        return all_jobs
    
    def create_job_dataframe(self, jobs: List[Dict]) -> pd.DataFrame:
        """
        创建招聘信息DataFrame
        
        Args:
            jobs: 招聘信息列表
            
        Returns:
            DataFrame
        """
        if not jobs:
            return pd.DataFrame()
        
        # 创建DataFrame
        df = pd.DataFrame(jobs)
        
        # 重新排列列顺序
        column_order = [
            'extraction_time', 'published_date', 'source', 'article_title',
            'company_name', 'job_title', 'department', 'location', 'employment_type',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period', 'salary_original',
            'requirements', 'responsibilities', 'benefits',
            'contact_person', 'contact_phone', 'contact_email', 'contact_wechat',
            'application_method', 'deadline', 'additional_info',
            'company_address', 'article_url', 'has_image_text', 'ai_confidence'
        ]
        
        # 确保所有列都存在
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[column_order]
        
        # 数据类型转换
        numeric_columns = ['salary_min', 'salary_max']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 日期格式化
        date_columns = ['extraction_time', 'published_date']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def generate_excel_report(self, jobs: List[Dict], filename: str = None) -> str:
        """
        生成Excel报告
        
        Args:
            jobs: 招聘信息列表
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"招聘信息汇总_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # 创建DataFrame
            df = self.create_job_dataframe(jobs)
            
            if df.empty:
                logger.warning("没有招聘信息可导出")
                return ""
            
            # 创建Excel写入器
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 主表：招聘信息
                df.to_excel(writer, sheet_name='招聘信息', index=False)
                
                # 统计表
                stats_data = {
                    '统计项': ['总职位数', '公司数量', '有薪资信息的职位', '有联系方式的职位'],
                    '数量': [
                        len(df),
                        df['company_name'].nunique(),
                        df['salary_min'].notna().sum(),
                        (df['contact_phone'] != '').sum() + (df['contact_email'] != '').sum()
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
                
                # 公司汇总
                company_stats = df.groupby('company_name').agg({
                    'job_title': 'count',
                    'location': lambda x: ', '.join(x.unique()),
                    'salary_min': 'mean',
                    'salary_max': 'mean'
                }).round(2)
                company_stats.columns = ['职位数', '工作地点', '平均最低薪资', '平均最高薪资']
                company_stats.to_excel(writer, sheet_name='公司汇总')
                
                # 职位分类
                job_stats = df.groupby('job_title').agg({
                    'company_name': 'count',
                    'salary_min': 'mean',
                    'salary_max': 'mean'
                }).round(2)
                job_stats.columns = ['公司数', '平均最低薪资', '平均最高薪资']
                job_stats.to_excel(writer, sheet_name='职位分类')
            
            logger.info(f"Excel报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成Excel报告失败: {e}")
            return ""
    
    def generate_csv_report(self, jobs: List[Dict], filename: str = None) -> str:
        """
        生成CSV报告
        
        Args:
            jobs: 招聘信息列表
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"招聘信息_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df = self.create_job_dataframe(jobs)
            
            if df.empty:
                logger.warning("没有招聘信息可导出")
                return ""
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"CSV报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成CSV报告失败: {e}")
            return ""
    
    def generate_json_report(self, jobs: List[Dict], filename: str = None) -> str:
        """
        生成JSON报告
        
        Args:
            jobs: 招聘信息列表
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"招聘信息_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            report_data = {
                'generated_at': datetime.now().isoformat(),
                'total_jobs': len(jobs),
                'jobs': jobs
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            return ""
    
    def process_articles_and_generate_reports(self, articles: List[Dict]) -> Dict:
        """
        处理文章并生成所有格式的报告
        
        Args:
            articles: 文章列表
            
        Returns:
            生成的报告文件路径
        """
        try:
            # 提取招聘信息
            jobs = self.extract_all_jobs(articles)
            
            if not jobs:
                logger.warning("没有找到招聘信息")
                return {
                    'success': False,
                    'message': '没有找到招聘信息',
                    'files': {}
                }
            
            # 生成不同格式的报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            files = {}
            
            # Excel报告
            excel_file = self.generate_excel_report(jobs, f"招聘信息汇总_{timestamp}.xlsx")
            if excel_file:
                files['excel'] = excel_file
            
            # CSV报告
            csv_file = self.generate_csv_report(jobs, f"招聘信息_{timestamp}.csv")
            if csv_file:
                files['csv'] = csv_file
            
            # JSON报告
            json_file = self.generate_json_report(jobs, f"招聘信息_{timestamp}.json")
            if json_file:
                files['json'] = json_file
            
            return {
                'success': True,
                'message': f'成功生成 {len(jobs)} 个招聘信息的报告',
                'job_count': len(jobs),
                'files': files
            }
            
        except Exception as e:
            logger.error(f"处理文章和生成报告失败: {e}")
            return {
                'success': False,
                'message': f'处理失败: {e}',
                'files': {}
            }


def test_job_extractor():
    """测试招聘信息提取器"""
    extractor = JobExtractor()
    
    # 测试数据
    test_articles = [
        {
            'title': '急招副导演',
            'source': '测试公众号',
            'published': '2024-01-01T00:00:00',
            'link': 'https://test.com/1',
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
                            'requirements': ['有相关经验', '熟悉影视制作流程'],
                            'responsibilities': ['协助导演工作', '现场执行']
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
    
    # 测试生成报告
    result = extractor.process_articles_and_generate_reports(test_articles)
    print(f"测试结果: {result}")


if __name__ == "__main__":
    test_job_extractor()