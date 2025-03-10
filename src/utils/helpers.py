import re
import os
import json
import datetime
import pandas as pd
import jieba
import jieba.analyse
from newspaper import Article
import yfinance as yf

from src.config import FOCUS_INDUSTRIES, POLICY_KEYWORDS, IMPORTANT_KEYWORDS

# 加载股票代码映射表
def load_stock_mapping():
    """
    加载股票代码映射表，如果不存在则创建一个空的映射表
    
    Returns:
        dict: 公司名称到股票代码的映射
    """
    mapping_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'data', 'stock_mapping.json')
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存股票代码映射表
def save_stock_mapping(mapping):
    """
    保存股票代码映射表
    
    Args:
        mapping (dict): 公司名称到股票代码的映射
    """
    mapping_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'data', 'stock_mapping.json')
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

# 查找公司对应的股票代码
def find_stock_code(company_name):
    """
    查找公司对应的股票代码
    
    Args:
        company_name (str): 公司名称
        
    Returns:
        str: 股票代码，如果找不到则返回空字符串
    """
    mapping = load_stock_mapping()
    
    # 直接查找
    if company_name in mapping:
        return mapping[company_name]
    
    # 尝试使用yfinance查找
    try:
        ticker = yf.Ticker(f"{company_name}")
        info = ticker.info
        if 'symbol' in info:
            code = info['symbol']
            mapping[company_name] = code
            save_stock_mapping(mapping)
            return code
    except:
        pass
    
    return ""

# 提取新闻中提到的公司
def extract_companies(text):
    """
    从文本中提取可能的公司名称
    
    Args:
        text (str): 新闻文本
        
    Returns:
        list: 可能的公司名称列表
    """
    # 这里使用一个简单的方法，实际应用中可能需要更复杂的NER模型
    companies = []
    
    # 常见的公司后缀
    suffixes = ['公司', '集团', '股份', '控股', '科技', '银行', '证券', '保险']
    
    # 使用jieba分词
    words = jieba.lcut(text)
    
    # 查找可能的公司名称
    for i, word in enumerate(words):
        if i < len(words) - 1 and any(suffix in words[i+1] for suffix in suffixes):
            companies.append(word + words[i+1])
        elif any(suffix in word for suffix in suffixes) and len(word) > 4:
            companies.append(word)
    
    return list(set(companies))

# 判断新闻是否与关注的行业相关
def is_industry_related(text):
    """
    判断新闻是否与关注的行业相关
    
    Args:
        text (str): 新闻文本
        
    Returns:
        bool: 是否相关
    """
    for industry in FOCUS_INDUSTRIES:
        if industry in text:
            return True
    return False

# 判断新闻是否包含政策信息
def contains_policy_info(text):
    """
    判断新闻是否包含政策信息
    
    Args:
        text (str): 新闻文本
        
    Returns:
        bool: 是否包含政策信息
    """
    for keyword in POLICY_KEYWORDS:
        if keyword in text:
            return True
    return False

# 判断新闻是否重要
def is_important_news(text):
    """
    判断新闻是否重要
    
    Args:
        text (str): 新闻文本
        
    Returns:
        bool: 是否重要
    """
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in text:
            return True
    return False

# 提取新闻关键词
def extract_keywords(text, top_k=5):
    """
    提取新闻关键词
    
    Args:
        text (str): 新闻文本
        top_k (int): 返回的关键词数量
        
    Returns:
        list: 关键词列表
    """
    return jieba.analyse.extract_tags(text, topK=top_k)

# 下载并解析新闻文章
def download_and_parse_article(url):
    """
    下载并解析新闻文章
    
    Args:
        url (str): 新闻URL
        
    Returns:
        dict: 包含标题、正文、发布日期等信息的字典
    """
    article = Article(url)
    try:
        article.download()
        article.parse()
        
        # 如果语言是中文，设置为中文
        if article.meta_lang == 'zh' or article.meta_lang == 'zh-cn':
            article.nlp(language='zh')
        else:
            article.nlp()
        
        return {
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date,
            'authors': article.authors,
            'summary': article.summary,
            'keywords': article.keywords,
            'url': url
        }
    except Exception as e:
        return {
            'title': '',
            'text': '',
            'publish_date': None,
            'authors': [],
            'summary': '',
            'keywords': [],
            'url': url,
            'error': str(e)
        }

# 格式化日期
def format_date(date_obj):
    """
    格式化日期
    
    Args:
        date_obj (datetime.datetime): 日期对象
        
    Returns:
        str: 格式化后的日期字符串
    """
    if date_obj is None:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return date_obj.strftime('%Y-%m-%d %H:%M:%S')

# 保存新闻数据
def save_news_data(news_data, filename):
    """
    保存新闻数据
    
    Args:
        news_data (list): 新闻数据列表
        filename (str): 文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

# 加载新闻数据
def load_news_data(filename):
    """
    加载新闻数据
    
    Args:
        filename (str): 文件名
        
    Returns:
        list: 新闻数据列表
    """
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] 