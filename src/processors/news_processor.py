import os
import json
from datetime import datetime

from src.utils.logger import setup_logger
from src.utils.helpers import (
    extract_companies, find_stock_code, is_industry_related,
    contains_policy_info, is_important_news, extract_keywords
)
from src.config import RAW_NEWS_DIR, PROCESSED_NEWS_DIR, FOCUS_INDUSTRIES

logger = setup_logger('news_processor')

class NewsProcessor:
    """
    新闻处理器，用于处理和分析新闻数据
    """
    
    def __init__(self):
        """
        初始化新闻处理器
        """
        self.logger = logger
    
    def process_news(self, news_list):
        """
        处理新闻列表
        
        Args:
            news_list (list): 新闻列表
            
        Returns:
            list: 处理后的新闻列表
        """
        processed_news = []
        
        for news in news_list:
            try:
                # 提取新闻内容
                title = news.get('title', '')
                content = news.get('content', '')
                
                # 如果没有内容，跳过
                if not title or not content:
                    continue
                
                # 合并标题和内容进行分析
                text = title + ' ' + content
                
                # 提取公司名称
                companies = extract_companies(text)
                
                # 查找公司对应的股票代码
                stock_codes = {}
                for company in companies:
                    code = find_stock_code(company)
                    if code:
                        stock_codes[company] = code
                
                # 判断是否与关注的行业相关
                industry_related = is_industry_related(text)
                
                # 判断是否包含政策信息
                policy_info = contains_policy_info(text)
                
                # 判断是否重要新闻
                important = is_important_news(text)
                
                # 提取关键词
                keywords = extract_keywords(text)
                
                # 判断新闻类型
                news_type = self._determine_news_type(text, policy_info, industry_related, important)
                
                # 相关行业
                related_industries = [industry for industry in FOCUS_INDUSTRIES if industry in text]
                
                # 创建处理后的新闻对象
                processed_item = {
                    'title': title,
                    'content': content,
                    'url': news.get('url', ''),
                    'publish_time': news.get('publish_time', ''),
                    'source': news.get('source', ''),
                    'companies': companies,
                    'stock_codes': stock_codes,
                    'industry_related': industry_related,
                    'policy_info': policy_info,
                    'important': important,
                    'keywords': keywords,
                    'news_type': news_type,
                    'related_industries': related_industries
                }
                
                processed_news.append(processed_item)
            except Exception as e:
                self.logger.error(f"处理新闻失败: {str(e)}")
        
        return processed_news
    
    def _determine_news_type(self, text, policy_info, industry_related, important):
        """
        确定新闻类型
        
        Args:
            text (str): 新闻文本
            policy_info (bool): 是否包含政策信息
            industry_related (bool): 是否与关注的行业相关
            important (bool): 是否重要新闻
            
        Returns:
            str: 新闻类型
        """
        if policy_info and industry_related:
            return '行业政策'
        elif policy_info:
            return '政策信息'
        elif industry_related and important:
            return '重要行业动态'
        elif industry_related:
            return '行业动态'
        elif important:
            return '重要新闻'
        else:
            return '一般新闻'
    
    def save_processed_news(self, processed_news):
        """
        保存处理后的新闻
        
        Args:
            processed_news (list): 处理后的新闻列表
            
        Returns:
            str: 保存的文件路径
        """
        # 创建文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"processed_news_{timestamp}.json"
        filepath = os.path.join(PROCESSED_NEWS_DIR, filename)
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_news, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"处理后的新闻已保存到: {filepath}")
        return filepath
    
    def filter_news(self, news_list, industry_only=False, policy_only=False, important_only=False):
        """
        过滤新闻
        
        Args:
            news_list (list): 新闻列表
            industry_only (bool, optional): 是否只返回与行业相关的新闻
            policy_only (bool, optional): 是否只返回政策相关的新闻
            important_only (bool, optional): 是否只返回重要新闻
            
        Returns:
            list: 过滤后的新闻列表
        """
        filtered_news = []
        
        for news in news_list:
            # 应用过滤条件
            if industry_only and not news.get('industry_related', False):
                continue
            
            if policy_only and not news.get('policy_info', False):
                continue
            
            if important_only and not news.get('important', False):
                continue
            
            filtered_news.append(news)
        
        return filtered_news
    
    def group_news_by_type(self, news_list):
        """
        按类型分组新闻
        
        Args:
            news_list (list): 新闻列表
            
        Returns:
            dict: 按类型分组的新闻
        """
        grouped_news = {}
        
        for news in news_list:
            news_type = news.get('news_type', '一般新闻')
            
            if news_type not in grouped_news:
                grouped_news[news_type] = []
            
            grouped_news[news_type].append(news)
        
        return grouped_news
    
    def group_news_by_industry(self, news_list):
        """
        按行业分组新闻
        
        Args:
            news_list (list): 新闻列表
            
        Returns:
            dict: 按行业分组的新闻
        """
        grouped_news = {}
        
        for news in news_list:
            related_industries = news.get('related_industries', [])
            
            if not related_industries:
                if '其他' not in grouped_news:
                    grouped_news['其他'] = []
                grouped_news['其他'].append(news)
                continue
            
            for industry in related_industries:
                if industry not in grouped_news:
                    grouped_news[industry] = []
                
                grouped_news[industry].append(news)
        
        return grouped_news 