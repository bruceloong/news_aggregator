from src.scrapers.base_scraper import BaseScraper
from src.scrapers.sina_scraper import SinaScraper
from src.scrapers.eastmoney_scraper import EastmoneyScraper

# 注册所有爬虫
SCRAPERS = {
    'sina': SinaScraper,
    'eastmoney': EastmoneyScraper,
}

def get_scraper(source_id):
    """
    获取指定ID的爬虫实例
    
    Args:
        source_id (str): 爬虫ID
        
    Returns:
        BaseScraper: 爬虫实例，如果不存在则返回None
    """
    scraper_class = SCRAPERS.get(source_id)
    if scraper_class:
        return scraper_class()
    return None

def get_all_scrapers():
    """
    获取所有爬虫实例
    
    Returns:
        list: 爬虫实例列表
    """
    return [scraper_class() for scraper_class in SCRAPERS.values()] 