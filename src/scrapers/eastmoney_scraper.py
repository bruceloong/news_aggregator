import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

from src.scrapers.base_scraper import BaseScraper

class EastmoneyScraper(BaseScraper):
    """
    东方财富爬虫
    """
    
    def __init__(self):
        """
        初始化东方财富爬虫
        """
        super().__init__('eastmoney', '东方财富', 'https://www.eastmoney.com/')
        
        # 东方财富的新闻API
        self.api_url = 'https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html'
        
        # 东方财富的新闻列表页
        self.news_list_urls = [
            'https://finance.eastmoney.com/a/cywjh.html',  # 财经要闻
            'https://finance.eastmoney.com/a/czqyw.html',  # 证券要闻
            'https://finance.eastmoney.com/a/cgsxw.html',  # 公司新闻
            'https://finance.eastmoney.com/a/cgspl.html',  # 公司评论
            'https://finance.eastmoney.com/a/chgyj.html',  # 行业研究
        ]
    
    def parse_api_news(self, hours=24):
        """
        解析API返回的新闻
        
        Args:
            hours (int): 抓取最近多少小时的新闻
            
        Returns:
            list: 新闻列表
        """
        news_list = []
        
        try:
            html = self.get_html(self.api_url)
            if not html:
                return news_list
            
            # 提取JSON数据
            json_str = re.search(r'var ajaxResult=(\{.*?\});', html)
            if not json_str:
                return news_list
            
            json_data = json.loads(json_str.group(1))
            news_items = json_data.get('LivesList', [])
            
            for item in news_items:
                try:
                    title = item.get('title', '')
                    content = item.get('digest', '')
                    url = item.get('url_unique', '')
                    time_str = item.get('showtime', '')
                    
                    # 判断是否是最近的新闻
                    if not self.is_recent(time_str, '%Y-%m-%d %H:%M:%S', hours):
                        continue
                    
                    news_list.append({
                        'title': title,
                        'content': content,
                        'url': url,
                        'publish_time': time_str,
                        'source': self.source_name
                    })
                except Exception as e:
                    self.logger.error(f"解析API新闻项失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"解析API新闻失败: {str(e)}")
        
        return news_list
    
    def parse_news_list(self, html):
        """
        解析新闻列表页
        
        Args:
            html (str): HTML内容
            
        Returns:
            list: 新闻列表
        """
        news_list = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找新闻列表
        news_items = soup.select('.news-item')
        
        for item in news_items:
            try:
                # 提取标题和URL
                a_tag = item.select_one('.news-item_title a')
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                url = a_tag['href']
                
                # 提取时间
                time_span = item.select_one('.news-item_time')
                if not time_span:
                    continue
                
                time_str = time_span.text.strip()
                
                # 判断是否是今天的新闻
                if not self.is_recent(time_str, '%Y-%m-%d %H:%M:%S'):
                    continue
                
                news_list.append({
                    'title': title,
                    'url': url,
                    'publish_time': time_str,
                    'source': self.source_name
                })
            except Exception as e:
                self.logger.error(f"解析新闻项失败: {str(e)}")
        
        return news_list
    
    def parse_news_detail(self, url):
        """
        解析新闻详情页
        
        Args:
            url (str): 新闻URL
            
        Returns:
            dict: 新闻详情
        """
        html = self.get_html(url)
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # 提取正文
            article = soup.select_one('.article-content')
            if not article:
                return {}
            
            # 移除不需要的元素
            for tag in article.select('script, style'):
                tag.decompose()
            
            content = article.get_text(strip=True)
            
            # 提取发布时间
            time_element = soup.select_one('.time')
            if time_element:
                publish_time = time_element.text.strip()
            else:
                publish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 提取作者
            author_element = soup.select_one('.source')
            author = author_element.text.strip() if author_element else ''
            
            return {
                'content': content,
                'publish_time': publish_time,
                'author': author
            }
        except Exception as e:
            self.logger.error(f"解析新闻详情失败: {url}, 错误: {str(e)}")
            return {}
    
    def scrape(self, hours=24):
        """
        抓取东方财富新闻
        
        Args:
            hours (int, optional): 抓取最近多少小时的新闻
            
        Returns:
            list: 新闻列表
        """
        self.logger.info(f"开始抓取东方财富新闻，最近{hours}小时")
        
        all_news = []
        
        # 抓取API新闻
        api_news = self.parse_api_news(hours)
        self.logger.info(f"从API抓取到 {len(api_news)} 条新闻")
        all_news.extend(api_news)
        
        # 抓取网页新闻
        for url in self.news_list_urls:
            try:
                self.logger.info(f"抓取新闻列表: {url}")
                html = self.get_html(url)
                if not html:
                    continue
                
                news_list = self.parse_news_list(html)
                self.logger.info(f"从 {url} 抓取到 {len(news_list)} 条新闻")
                
                # 抓取新闻详情
                for news in news_list:
                    try:
                        self.logger.info(f"抓取新闻详情: {news['url']}")
                        detail = self.parse_news_detail(news['url'])
                        if detail:
                            news.update(detail)
                            all_news.append(news)
                    except Exception as e:
                        self.logger.error(f"抓取新闻详情失败: {news['url']}, 错误: {str(e)}")
            except Exception as e:
                self.logger.error(f"抓取新闻列表失败: {url}, 错误: {str(e)}")
        
        self.logger.info(f"共抓取到 {len(all_news)} 条东方财富新闻")
        return all_news 