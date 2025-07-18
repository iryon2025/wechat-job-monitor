#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR图片识别模块
使用PaddleOCR进行图片文字识别
"""

import os
import logging
from typing import List, Dict, Optional, Union
import json
from PIL import Image
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    logger.warning("PaddleOCR未安装，请运行: pip install paddleocr")
    PADDLEOCR_AVAILABLE = False


class OCRProcessor:
    """OCR处理器，负责图片文字识别"""
    
    def __init__(self, use_gpu: bool = False, lang: str = 'ch'):
        """
        初始化OCR处理器
        
        Args:
            use_gpu: 是否使用GPU
            lang: 语言设置，'ch'为中文
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self.ocr = None
        
        if PADDLEOCR_AVAILABLE:
            try:
                # 初始化PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,  # 使用角度分类器
                    lang=lang,          # 语言
                    use_gpu=use_gpu,    # 是否使用GPU
                    show_log=False      # 不显示日志
                )
                logger.info(f"PaddleOCR初始化成功，语言: {lang}, GPU: {use_gpu}")
            except Exception as e:
                logger.error(f"PaddleOCR初始化失败: {e}")
                self.ocr = None
        else:
            logger.error("PaddleOCR不可用")
    
    def is_available(self) -> bool:
        """
        检查OCR是否可用
        
        Returns:
            是否可用
        """
        return self.ocr is not None
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        预处理图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            预处理后的图片数组
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return None
            
            # 使用PIL打开图片
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 转换为numpy数组
                img_array = np.array(img)
                
                # 检查图片尺寸
                height, width = img_array.shape[:2]
                if height < 10 or width < 10:
                    logger.warning(f"图片尺寸过小: {width}x{height}")
                    return None
                
                # 如果图片过大，进行缩放
                max_size = 2048
                if max(height, width) > max_size:
                    scale = max_size / max(height, width)
                    new_height = int(height * scale)
                    new_width = int(width * scale)
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    img_array = np.array(img_resized)
                    logger.info(f"图片已缩放: {width}x{height} -> {new_width}x{new_height}")
                
                return img_array
                
        except Exception as e:
            logger.error(f"预处理图片失败 {image_path}: {e}")
            return None
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别结果字典
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'OCR不可用',
                'text': '',
                'details': []
            }
        
        try:
            logger.info(f"开始识别图片: {image_path}")
            
            # 预处理图片
            img_array = self.preprocess_image(image_path)
            if img_array is None:
                return {
                    'success': False,
                    'error': '图片预处理失败',
                    'text': '',
                    'details': []
                }
            
            # 执行OCR识别
            result = self.ocr.ocr(img_array, cls=True)
            
            if not result or not result[0]:
                return {
                    'success': True,
                    'text': '',
                    'details': [],
                    'message': '图片中未检测到文字'
                }
            
            # 解析识别结果
            extracted_text = []
            text_details = []
            
            for line in result[0]:
                if line:
                    # 获取文字位置和内容
                    bbox = line[0]  # 边界框坐标
                    text_info = line[1]  # 文字信息
                    
                    if text_info and len(text_info) >= 2:
                        text = text_info[0]  # 识别的文字
                        confidence = text_info[1]  # 置信度
                        
                        if text and confidence > 0.5:  # 过滤置信度低的结果
                            extracted_text.append(text)
                            text_details.append({
                                'text': text,
                                'confidence': confidence,
                                'bbox': bbox
                            })
            
            # 合并所有文字
            full_text = '\n'.join(extracted_text)
            
            logger.info(f"识别完成，共识别到 {len(extracted_text)} 行文字")
            
            return {
                'success': True,
                'text': full_text,
                'details': text_details,
                'line_count': len(extracted_text),
                'image_path': image_path
            }
            
        except Exception as e:
            logger.error(f"图片识别失败 {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'details': []
            }
    
    def extract_text_from_images(self, image_paths: List[str]) -> List[Dict]:
        """
        批量处理多张图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            识别结果列表
        """
        results = []
        
        for image_path in image_paths:
            result = self.extract_text_from_image(image_path)
            results.append(result)
        
        logger.info(f"批量识别完成，共处理 {len(image_paths)} 张图片")
        return results
    
    def filter_job_related_text(self, text: str) -> Dict:
        """
        过滤和提取招聘相关的文字信息
        
        Args:
            text: 识别的文字
            
        Returns:
            过滤结果
        """
        if not text:
            return {
                'is_job_related': False,
                'job_keywords': [],
                'filtered_text': '',
                'confidence': 0.0
            }
        
        # 招聘相关关键词
        job_keywords = [
            # 职位相关
            '招聘', '求职', '职位', '岗位', '工作', '面试', '简历', '人才',
            '应聘', '录用', '入职', '试用', '转正', '晋升', 
            
            # 薪资福利
            '薪资', '工资', '薪水', '待遇', '福利', '五险一金', '年薪', '月薪',
            '奖金', '提成', '补贴', '津贴', '保险', '公积金',
            
            # 工作类型
            '全职', '兼职', '实习', '临时', '合同', '正式', '试用期',
            '远程', '居家', '驻场', '出差', '外派',
            
            # 影视行业特定
            '副导演', '导演', '制片', '摄影', '剪辑', '后期', '编导',
            '影视', '传媒', '广告', '制作', '策划', '文案', '运营',
            '摄像', '录音', '灯光', '美术', '化妆', '服装', '道具',
            '场记', '统筹', '制片人', '监制', '编剧', '配音', '特效',
            
            # 技能要求
            '经验', '学历', '专业', '技能', '能力', '熟练', '精通',
            '本科', '专科', '硕士', '年以上', '相关经验',
            
            # 联系方式
            '联系', '电话', '微信', '邮箱', '地址', '简历发送',
            '有意者', '请联系', '咨询', '报名'
        ]
        
        # 统计关键词出现次数
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in job_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        # 计算相关性得分
        relevance_score = len(found_keywords) / len(job_keywords) if job_keywords else 0
        
        # 判断是否与招聘相关
        is_job_related = len(found_keywords) >= 2  # 至少包含2个关键词
        
        # 提取包含关键词的句子
        sentences = text.split('\n')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in found_keywords):
                relevant_sentences.append(sentence.strip())
        
        filtered_text = '\n'.join(relevant_sentences) if relevant_sentences else text
        
        return {
            'is_job_related': is_job_related,
            'job_keywords': found_keywords,
            'filtered_text': filtered_text,
            'confidence': relevance_score,
            'keyword_count': len(found_keywords),
            'total_keywords': len(job_keywords)
        }
    
    def process_article_images(self, article: Dict) -> Dict:
        """
        处理文章中的所有图片
        
        Args:
            article: 文章信息
            
        Returns:
            处理后的文章信息
        """
        if not article.get('images'):
            return article
        
        logger.info(f"开始处理文章图片: {article.get('title', 'Unknown')}")
        
        ocr_results = []
        all_image_text = []
        
        for image_info in article['images']:
            local_path = image_info.get('local_path')
            if not local_path or not os.path.exists(local_path):
                logger.warning(f"图片文件不存在: {local_path}")
                continue
            
            # 执行OCR识别
            ocr_result = self.extract_text_from_image(local_path)
            
            if ocr_result['success'] and ocr_result['text']:
                # 过滤招聘相关文字
                filtered_result = self.filter_job_related_text(ocr_result['text'])
                
                ocr_result.update(filtered_result)
                ocr_results.append(ocr_result)
                
                if filtered_result['is_job_related']:
                    all_image_text.append(filtered_result['filtered_text'])
                    logger.info(f"发现招聘相关图片文字: {len(filtered_result['job_keywords'])} 个关键词")
        
        # 合并所有图片的文字
        combined_image_text = '\n'.join(all_image_text)
        
        # 更新文章信息
        article['ocr_results'] = ocr_results
        article['image_text'] = combined_image_text
        article['has_job_images'] = len(all_image_text) > 0
        
        logger.info(f"图片处理完成: {len(ocr_results)} 张图片，{len(all_image_text)} 张包含招聘信息")
        
        return article
    
    def save_ocr_results(self, results: List[Dict], output_file: str):
        """
        保存OCR识别结果
        
        Args:
            results: 识别结果列表
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"OCR结果已保存到: {output_file}")
        except Exception as e:
            logger.error(f"保存OCR结果失败: {e}")


def test_ocr_processor():
    """测试OCR处理器"""
    processor = OCRProcessor()
    
    if not processor.is_available():
        print("OCR处理器不可用")
        return
    
    # 测试图片路径
    test_image = "test_image.jpg"
    
    if os.path.exists(test_image):
        result = processor.extract_text_from_image(test_image)
        print(f"识别结果: {result}")
    else:
        print(f"测试图片不存在: {test_image}")


if __name__ == "__main__":
    test_ocr_processor()