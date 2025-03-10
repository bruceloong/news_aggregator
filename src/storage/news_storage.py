import os
import json
from datetime import datetime

from src.utils.logger import setup_logger
from src.config import RAW_NEWS_DIR, PROCESSED_NEWS_DIR

logger = setup_logger('news_storage')

class NewsStorage:
    """
    新闻存储类，用于保存和加载新闻数据
    """
    
    def __init__(self):
        """
        初始化新闻存储
        """
        self.logger = logger
    
    def save_raw_news(self, news_list, source_id):
        """
        保存原始新闻数据
        
        Args:
            news_list (list): 新闻列表
            source_id (str): 新闻源ID
            
        Returns:
            str: 保存的文件路径
        """
        # 创建文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"raw_news_{source_id}_{timestamp}.json"
        filepath = os.path.join(RAW_NEWS_DIR, filename)
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"原始新闻已保存到: {filepath}")
        return filepath
    
    def load_raw_news(self, filepath):
        """
        加载原始新闻数据
        
        Args:
            filepath (str): 文件路径
            
        Returns:
            list: 新闻列表
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                news_list = json.load(f)
            
            self.logger.info(f"已加载原始新闻: {filepath}")
            return news_list
        except Exception as e:
            self.logger.error(f"加载原始新闻失败: {filepath}, 错误: {str(e)}")
            return []
    
    def save_processed_news(self, news_list):
        """
        保存处理后的新闻数据
        
        Args:
            news_list (list): 新闻列表
            
        Returns:
            str: 保存的文件路径
        """
        # 创建文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"processed_news_{timestamp}.json"
        filepath = os.path.join(PROCESSED_NEWS_DIR, filename)
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"处理后的新闻已保存到: {filepath}")
        return filepath
    
    def load_processed_news(self, filepath):
        """
        加载处理后的新闻数据
        
        Args:
            filepath (str): 文件路径
            
        Returns:
            list: 新闻列表
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                news_list = json.load(f)
            
            self.logger.info(f"已加载处理后的新闻: {filepath}")
            return news_list
        except Exception as e:
            self.logger.error(f"加载处理后的新闻失败: {filepath}, 错误: {str(e)}")
            return []
    
    def get_latest_raw_news(self, source_id=None):
        """
        获取最新的原始新闻数据
        
        Args:
            source_id (str, optional): 新闻源ID，如果为None则返回所有源的最新新闻
            
        Returns:
            list: 新闻列表
        """
        # 获取所有原始新闻文件
        files = os.listdir(RAW_NEWS_DIR)
        
        # 过滤文件
        if source_id:
            files = [f for f in files if f.startswith(f"raw_news_{source_id}_")]
        else:
            files = [f for f in files if f.startswith("raw_news_")]
        
        if not files:
            return []
        
        # 按时间排序
        files.sort(reverse=True)
        
        # 加载最新的文件
        return self.load_raw_news(os.path.join(RAW_NEWS_DIR, files[0]))
    
    def get_latest_processed_news(self):
        """
        获取最新的处理后的新闻数据
        
        Returns:
            list: 新闻列表
        """
        # 获取所有处理后的新闻文件
        files = os.listdir(PROCESSED_NEWS_DIR)
        
        # 过滤文件
        files = [f for f in files if f.startswith("processed_news_")]
        
        if not files:
            return []
        
        # 按时间排序
        files.sort(reverse=True)
        
        # 加载最新的文件
        return self.load_processed_news(os.path.join(PROCESSED_NEWS_DIR, files[0]))
    
    def get_all_raw_news(self, hours=24):
        """
        获取所有原始新闻数据
        
        Args:
            hours (int, optional): 获取最近多少小时的新闻
            
        Returns:
            list: 新闻列表
        """
        all_news = []
        
        # 获取所有原始新闻文件
        files = os.listdir(RAW_NEWS_DIR)
        
        # 过滤文件
        files = [f for f in files if f.startswith("raw_news_")]
        
        if not files:
            return []
        
        # 计算时间阈值
        now = datetime.now()
        threshold = now - datetime.timedelta(hours=hours)
        
        # 遍历文件
        for file in files:
            try:
                # 从文件名中提取时间
                time_str = file.split('_')[2].split('.')[0]
                file_time = datetime.strptime(time_str, '%Y%m%d')
                
                # 如果文件时间在阈值之后，加载文件
                if file_time >= threshold:
                    news_list = self.load_raw_news(os.path.join(RAW_NEWS_DIR, file))
                    all_news.extend(news_list)
            except Exception as e:
                self.logger.error(f"处理文件失败: {file}, 错误: {str(e)}")
        
        return all_news 