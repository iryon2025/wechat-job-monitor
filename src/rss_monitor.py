#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS监控模块
用于监控微信公众号RSS源，获取最新文章
"""

import feedparser
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import logging
from bs4 import BeautifulSoup
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSMonitor:
    """RSS监控器，负责获取和解析微信公众号RSS源"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化RSS监控器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.last_check_file = os.path.join(data_dir, "last_check.json")
        self.articles_cache_file = os.path.join(data_dir, "articles_cache.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def load_rss_sources(self, config_file: str = "config/rss_sources.json") -> List[Dict]:
        """
        加载RSS源配置
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            RSS源列表
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                sources = json.load(f)
                logger.info(f"加载了 {len(sources)} 个RSS源")
                return sources
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 不存在")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return []
    
    def get_last_check_time(self) -> datetime:
        """
        获取上次检查时间
        
        Returns:
            上次检查时间
        """
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_check'])
            else:
                # 如果没有记录，返回24小时前的时间
                return datetime.now() - timedelta(hours=24)
        except Exception as e:
            logger.error(f"读取上次检查时间失败: {e}")
            return datetime.now() - timedelta(hours=24)
    
    def save_last_check_time(self, check_time: datetime):
        """
        保存检查时间
        
        Args:
            check_time: 检查时间
        """
        try:
            data = {'last_check': check_time.isoformat()}
            with open(self.last_check_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存检查时间失败: {e}")
    
    def fetch_rss_feed(self, rss_url: str, timeout: int = 30) -> Optional[feedparser.FeedParserDict]:
        """
        获取RSS源内容
        
        Args:
            rss_url: RSS地址
            timeout: 超时时间
            
        Returns:
            RSS解析结果
        """
        try:
            logger.info(f"正在获取RSS源: {rss_url}")
            
            # 使用requests获取RSS内容
            response = requests.get(rss_url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            
            # 解析RSS内容
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS源可能有格式问题: {rss_url}")
            
            logger.info(f"成功获取 {len(feed.entries)} 篇文章")
            return feed
            
        except requests.RequestException as e:
            logger.error(f"获取RSS源失败 {rss_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"解析RSS源失败 {rss_url}: {e}")
            return None
    
    def parse_article_content(self, entry) -> Dict:
        """
        解析文章内容
        
        Args:
            entry: RSS条目
            
        Returns:
            解析后的文章信息
        """
        try:
            # 获取文章基本信息
            title = entry.title if hasattr(entry, 'title') else "无标题"
            link = entry.link if hasattr(entry, 'link') else ""
            summary = entry.summary if hasattr(entry, 'summary') else ""
            
            # 解析发布时间
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                try:
                    published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    published = datetime.now()
            else:
                published = datetime.now()
            
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(summary, 'html.parser')
            
            # 提取纯文本内容
            text_content = soup.get_text(strip=True)
            
            # 提取图片链接
            images = []
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if src:
                    images.append({
                        'url': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            # 检查是否包含招聘相关关键词
            job_keywords = [
                '招聘', '求职', '职位', '岗位', '工作', '面试', '简历', 
                '薪资', '工资', '待遇', '福利', '全职', '兼职', '实习',
                '副导演', '导演', '制片', '摄影', '剪辑', '后期', '编导',
                '影视', '传媒', '广告', '制作', '策划', '文案', '运营'
            ]
            
            is_job_related = any(keyword in text_content or keyword in title 
                               for keyword in job_keywords)
            
            article = {
                'title': title,
                'link': link,
                'summary': text_content[:500] + '...' if len(text_content) > 500 else text_content,
                'full_content': text_content,
                'published': published.isoformat(),
                'images': images,
                'is_job_related': is_job_related,
                'source': entry.get('source', {}).get('title', '未知来源'),
                'guid': entry.get('id', link)  # 唯一标识符
            }
            
            return article
            
        except Exception as e:
            logger.error(f"解析文章内容失败: {e}")
            return {}
    
    def download_image(self, image_url: str, save_dir: str = None) -> Optional[str]:
        """
        下载图片到本地
        
        Args:
            image_url: 图片URL
            save_dir: 保存目录
            
        Returns:
            本地图片路径
        """
        try:
            if not save_dir:
                save_dir = os.path.join(self.data_dir, "images")
                os.makedirs(save_dir, exist_ok=True)
            
            # 生成文件名
            filename = f"img_{int(time.time())}_{hash(image_url) % 10000}.jpg"
            file_path = os.path.join(save_dir, filename)
            
            # 下载图片
            response = requests.get(image_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片下载成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"下载图片失败 {image_url}: {e}")
            return None
    
    def get_new_articles(self, rss_sources: List[Dict], since_time: datetime = None) -> List[Dict]:
        """
        获取新文章
        
        Args:
            rss_sources: RSS源列表
            since_time: 开始时间
            
        Returns:
            新文章列表
        """
        if since_time is None:
            since_time = self.get_last_check_time()
        
        all_new_articles = []
        
        for source in rss_sources:
            try:
                source_name = source.get('name', '未知来源')
                rss_url = source.get('url', '')
                
                if not rss_url:
                    logger.warning(f"跳过无效的RSS源: {source_name}")
                    continue
                
                logger.info(f"正在检查RSS源: {source_name}")
                
                # 获取RSS内容
                feed = self.fetch_rss_feed(rss_url)
                if not feed:
                    continue
                
                # 解析文章
                for entry in feed.entries:
                    article = self.parse_article_content(entry)
                    if not article:
                        continue
                    
                    # 检查文章发布时间
                    article_time = datetime.fromisoformat(article['published'])
                    if article_time > since_time:
                        article['source'] = source_name
                        article['rss_url'] = rss_url
                        
                        # 下载图片
                        for i, image in enumerate(article['images']):
                            local_path = self.download_image(image['url'])
                            if local_path:
                                article['images'][i]['local_path'] = local_path
                        
                        all_new_articles.append(article)
                        logger.info(f"发现新文章: {article['title']}")
                
            except Exception as e:
                logger.error(f"处理RSS源 {source.get('name', 'unknown')} 失败: {e}")
                continue
        
        # 按发布时间排序
        all_new_articles.sort(key=lambda x: x['published'], reverse=True)
        
        logger.info(f"共发现 {len(all_new_articles)} 篇新文章")
        return all_new_articles
    
    def save_articles_cache(self, articles: List[Dict]):
        """
        保存文章缓存
        
        Args:
            articles: 文章列表
        """
        try:
            with open(self.articles_cache_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(articles)} 篇文章到缓存")
        except Exception as e:
            logger.error(f"保存文章缓存失败: {e}")
    
    def load_articles_cache(self) -> List[Dict]:
        """
        加载文章缓存
        
        Returns:
            缓存的文章列表
        """
        try:
            if os.path.exists(self.articles_cache_file):
                with open(self.articles_cache_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    logger.info(f"加载了 {len(articles)} 篇缓存文章")
                    return articles
            return []
        except Exception as e:
            logger.error(f"加载文章缓存失败: {e}")
            return []
    
    def monitor_rss_sources(self, config_file: str = "config/rss_sources.json") -> List[Dict]:
        """
        监控RSS源，获取新文章
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            新文章列表
        """
        try:
            logger.info("开始监控RSS源...")
            
            # 加载RSS源配置
            rss_sources = self.load_rss_sources(config_file)
            if not rss_sources:
                logger.error("没有可用的RSS源")
                return []
            
            # 获取上次检查时间
            last_check = self.get_last_check_time()
            logger.info(f"上次检查时间: {last_check}")
            
            # 获取新文章
            new_articles = self.get_new_articles(rss_sources, last_check)
            
            # 保存文章缓存
            if new_articles:
                self.save_articles_cache(new_articles)
            
            # 更新检查时间
            self.save_last_check_time(datetime.now())
            
            logger.info(f"RSS监控完成，共发现 {len(new_articles)} 篇新文章")
            return new_articles
            
        except Exception as e:
            logger.error(f"RSS监控失败: {e}")
            return []


if __name__ == "__main__":
    # 测试代码
    monitor = RSSMonitor()
    articles = monitor.monitor_rss_sources()
    
    if articles:
        print(f"发现 {len(articles)} 篇新文章:")
        for article in articles:
            print(f"- {article['title']} ({article['source']})")
    else:
        print("没有发现新文章")