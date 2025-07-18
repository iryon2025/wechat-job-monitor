#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容分析模块
使用DeepSeek API进行文本内容分析和总结
"""

import json
import logging
import os
from typing import Dict, List, Optional
import requests
from datetime import datetime
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """内容分析器，使用DeepSeek API进行文本分析"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        """
        初始化内容分析器
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url
        self.model = "deepseek-chat"
        
        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("DeepSeek API密钥未设置")
    
    def is_available(self) -> bool:
        """
        检查API是否可用
        
        Returns:
            是否可用
        """
        return self.api_key is not None
    
    def call_deepseek_api(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> Optional[Dict]:
        """
        调用DeepSeek API
        
        Args:
            messages: 消息列表
            max_tokens: 最大令牌数
            temperature: 随机性控制
            
        Returns:
            API响应结果
        """
        if not self.is_available():
            logger.error("DeepSeek API不可用")
            return None
        
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            logger.info(f"调用DeepSeek API: {url}")
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result
            else:
                logger.error(f"API响应格式异常: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"API响应解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"API调用异常: {e}")
            return None
    
    def summarize_article(self, article: Dict) -> Dict:
        """
        总结文章内容
        
        Args:
            article: 文章信息
            
        Returns:
            总结结果
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DeepSeek API不可用',
                'summary': ''
            }
        
        try:
            title = article.get('title', '')
            content = article.get('full_content', '')
            image_text = article.get('image_text', '')
            
            # 构建分析内容
            analysis_content = f"""
文章标题: {title}

文章内容:
{content}

图片文字:
{image_text}
"""
            
            # 构建提示词
            system_prompt = """你是一个专业的招聘信息分析助手。请分析以下微信公众号文章内容，判断是否包含招聘信息，并提供详细的总结。

请按以下格式回复：
1. 是否包含招聘信息（是/否）
2. 文章主题总结（1-2句话）
3. 如果包含招聘信息，请提取：
   - 招聘岗位
   - 公司/机构名称
   - 工作地点
   - 薪资待遇
   - 任职要求
   - 联系方式
4. 重要信息摘要（3-5个要点）"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_content}
            ]
            
            # 调用API
            result = self.call_deepseek_api(messages, max_tokens=1500, temperature=0.3)
            
            if result and 'choices' in result:
                summary = result['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'summary': summary,
                    'usage': result.get('usage', {}),
                    'model': self.model
                }
            else:
                return {
                    'success': False,
                    'error': 'API响应异常',
                    'summary': ''
                }
                
        except Exception as e:
            logger.error(f"文章总结失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': ''
            }
    
    def extract_job_info(self, article: Dict) -> Dict:
        """
        提取招聘信息
        
        Args:
            article: 文章信息
            
        Returns:
            提取结果
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DeepSeek API不可用',
                'job_info': {}
            }
        
        try:
            title = article.get('title', '')
            content = article.get('full_content', '')
            image_text = article.get('image_text', '')
            
            # 构建分析内容
            analysis_content = f"""
文章标题: {title}

文章内容:
{content}

图片文字:
{image_text}
"""
            
            # 构建提示词
            system_prompt = """你是一个专业的招聘信息提取助手。请从以下内容中提取结构化的招聘信息。

请严格按照以下JSON格式回复，如果某个字段没有信息则填写"未提及"：
{
    "is_job_posting": true/false,
    "company_name": "公司名称",
    "positions": [
        {
            "job_title": "职位名称",
            "department": "部门",
            "location": "工作地点",
            "salary": "薪资待遇",
            "employment_type": "全职/兼职/实习",
            "requirements": [
                "任职要求1",
                "任职要求2"
            ],
            "responsibilities": [
                "工作职责1",
                "工作职责2"
            ],
            "benefits": [
                "福利待遇1",
                "福利待遇2"
            ]
        }
    ],
    "contact_info": {
        "contact_person": "联系人",
        "phone": "联系电话",
        "email": "邮箱地址",
        "wechat": "微信号",
        "address": "公司地址",
        "application_method": "应聘方式"
    },
    "deadline": "截止日期",
    "additional_info": "其他重要信息"
}

请确保返回的是有效的JSON格式。"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_content}
            ]
            
            # 调用API
            result = self.call_deepseek_api(messages, max_tokens=2000, temperature=0.1)
            
            if result and 'choices' in result:
                response_content = result['choices'][0]['message']['content']
                
                # 尝试解析JSON
                try:
                    # 提取JSON部分
                    json_start = response_content.find('{')
                    json_end = response_content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_content[json_start:json_end]
                        job_info = json.loads(json_str)
                        
                        return {
                            'success': True,
                            'job_info': job_info,
                            'raw_response': response_content,
                            'usage': result.get('usage', {})
                        }
                    else:
                        logger.warning("响应中未找到有效的JSON格式")
                        return {
                            'success': False,
                            'error': 'JSON格式解析失败',
                            'job_info': {},
                            'raw_response': response_content
                        }
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    return {
                        'success': False,
                        'error': f'JSON解析失败: {e}',
                        'job_info': {},
                        'raw_response': response_content
                    }
            else:
                return {
                    'success': False,
                    'error': 'API响应异常',
                    'job_info': {}
                }
                
        except Exception as e:
            logger.error(f"招聘信息提取失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'job_info': {}
            }
    
    def analyze_job_relevance(self, text: str) -> Dict:
        """
        分析文本的招聘相关性
        
        Args:
            text: 待分析文本
            
        Returns:
            相关性分析结果
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DeepSeek API不可用',
                'relevance_score': 0.0
            }
        
        try:
            system_prompt = """你是一个专业的文本分析助手。请分析以下文本是否与招聘求职相关，并给出相关性评分。

请按以下格式回复：
1. 相关性评分（0-1之间的数字，0表示完全不相关，1表示高度相关）
2. 主要原因（简短说明）
3. 关键词列表（提取到的相关关键词）"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
            
            result = self.call_deepseek_api(messages, max_tokens=500, temperature=0.2)
            
            if result and 'choices' in result:
                response = result['choices'][0]['message']['content']
                
                # 简单解析评分
                score = 0.0
                try:
                    lines = response.split('\n')
                    for line in lines:
                        if '评分' in line or '分' in line:
                            import re
                            score_match = re.search(r'(\d+\.?\d*)', line)
                            if score_match:
                                score = float(score_match.group(1))
                                if score > 1:
                                    score = score / 10  # 如果是0-10分制，转换为0-1
                                break
                except:
                    pass
                
                return {
                    'success': True,
                    'relevance_score': score,
                    'analysis': response,
                    'usage': result.get('usage', {})
                }
            else:
                return {
                    'success': False,
                    'error': 'API响应异常',
                    'relevance_score': 0.0
                }
                
        except Exception as e:
            logger.error(f"相关性分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'relevance_score': 0.0
            }
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        批量处理文章
        
        Args:
            articles: 文章列表
            
        Returns:
            处理后的文章列表
        """
        if not self.is_available():
            logger.error("DeepSeek API不可用，跳过内容分析")
            return articles
        
        processed_articles = []
        
        for i, article in enumerate(articles):
            try:
                logger.info(f"正在分析文章 {i+1}/{len(articles)}: {article.get('title', 'Unknown')}")
                
                # 文章总结
                summary_result = self.summarize_article(article)
                article['ai_summary'] = summary_result
                
                # 如果文章可能包含招聘信息，进行详细提取
                if (article.get('is_job_related', False) or 
                    article.get('has_job_images', False) or 
                    '招聘' in article.get('title', '')):
                    
                    job_info_result = self.extract_job_info(article)
                    article['job_extraction'] = job_info_result
                    
                    # 更新招聘相关标记
                    if job_info_result.get('success') and job_info_result.get('job_info', {}).get('is_job_posting'):
                        article['is_confirmed_job_posting'] = True
                    else:
                        article['is_confirmed_job_posting'] = False
                else:
                    article['is_confirmed_job_posting'] = False
                
                processed_articles.append(article)
                
                # 添加延迟，避免API请求过于频繁
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"处理文章失败: {e}")
                processed_articles.append(article)
                continue
        
        logger.info(f"文章分析完成，共处理 {len(processed_articles)} 篇文章")
        return processed_articles
    
    def generate_summary_report(self, articles: List[Dict]) -> Dict:
        """
        生成总结报告
        
        Args:
            articles: 文章列表
            
        Returns:
            总结报告
        """
        try:
            total_articles = len(articles)
            job_related_articles = len([a for a in articles if a.get('is_job_related', False)])
            confirmed_job_postings = len([a for a in articles if a.get('is_confirmed_job_posting', False)])
            articles_with_images = len([a for a in articles if a.get('has_job_images', False)])
            
            # 提取所有职位信息
            all_positions = []
            for article in articles:
                job_extraction = article.get('job_extraction', {})
                if job_extraction.get('success') and job_extraction.get('job_info', {}).get('positions'):
                    positions = job_extraction['job_info']['positions']
                    for position in positions:
                        position['article_title'] = article.get('title', '')
                        position['source'] = article.get('source', '')
                        position['published'] = article.get('published', '')
                        all_positions.append(position)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': {
                    'total_articles': total_articles,
                    'job_related_articles': job_related_articles,
                    'confirmed_job_postings': confirmed_job_postings,
                    'articles_with_job_images': articles_with_images,
                    'total_positions': len(all_positions)
                },
                'positions': all_positions,
                'articles': articles
            }
            
            logger.info(f"生成总结报告: {total_articles} 篇文章, {confirmed_job_postings} 篇确认的招聘信息")
            return report
            
        except Exception as e:
            logger.error(f"生成总结报告失败: {e}")
            return {
                'generated_at': datetime.now().isoformat(),
                'error': str(e),
                'statistics': {},
                'positions': [],
                'articles': articles
            }


def test_content_analyzer():
    """测试内容分析器"""
    # 需要设置环境变量 DEEPSEEK_API_KEY
    analyzer = ContentAnalyzer()
    
    if not analyzer.is_available():
        print("DeepSeek API不可用，请设置环境变量 DEEPSEEK_API_KEY")
        return
    
    # 测试文本
    test_text = """
    招聘副导演一名
    工作地点：北京
    薪资：8000-12000元/月
    要求：有相关经验，熟悉影视制作流程
    联系电话：13800138000
    """
    
    # 测试相关性分析
    relevance_result = analyzer.analyze_job_relevance(test_text)
    print(f"相关性分析结果: {relevance_result}")


if __name__ == "__main__":
    test_content_analyzer()