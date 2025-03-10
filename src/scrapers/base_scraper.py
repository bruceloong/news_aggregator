import requests
from datetime import datetime, timedelta
import time
import random
from abc import ABC, abstractmethod

from src.utils.logger import setup_logger

class BaseScraper(ABC):
    """
    新闻爬虫的基类，定义了爬虫的基本接口和通用方法
    """
    
    def __init__(self, source_id, source_name, source_url):
        """
        初始化爬虫
        
        Args:
            source_id (str): 新闻源ID
            source_name (str): 新闻源名称
            source_url (str): 新闻源URL
        """
        self.source_id = source_id
        self.source_name = source_name
        self.source_url = source_url
        self.logger = setup_logger(f"scraper_{source_id}")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def get_html(self, url, params=None, retries=3):
        """
        获取网页HTML内容
        
        Args:
            url (str): 网页URL
            params (dict, optional): 请求参数
            retries (int, optional): 重试次数
            
        Returns:
            str: HTML内容，如果获取失败则返回空字符串
        """
        for i in range(retries):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                self.logger.error(f"获取HTML失败 ({i+1}/{retries}): {url}, 错误: {str(e)}")
                if i < retries - 1:
                    # 随机等待1-3秒后重试
                    time.sleep(random.uniform(1, 3))
        return ""
    
    def is_recent(self, date_str, date_format, hours=24):
        """
        判断日期是否在最近的指定小时内
        
        Args:
            date_str (str): 日期字符串
            date_format (str): 日期格式
            hours (int, optional): 小时数
            
        Returns:
            bool: 是否在最近的指定小时内
        """
        try:
            date = datetime.strptime(date_str, date_format)
            now = datetime.now()
            delta = now - date
            return delta <= timedelta(hours=hours)
        except Exception as e:
            self.logger.error(f"日期解析失败: {date_str}, 格式: {date_format}, 错误: {str(e)}")
            return False
    
    @abstractmethod
    def scrape(self, hours=24):
        """
        抓取新闻
        
        Args:
            hours (int, optional): 抓取最近多少小时的新闻
            
        Returns:
            list: 新闻列表，每个元素为一个字典，包含标题、URL、发布时间等信息
        """
        pass 