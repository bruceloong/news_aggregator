import re
from bs4 import BeautifulSoup
from datetime import datetime

from src.scrapers.base_scraper import BaseScraper

class SinaScraper(BaseScraper):
    """
    新浪财经爬虫
    """
    
    def __init__(self):
        """
        初始化新浪财经爬虫
        """
        super().__init__('sina', '新浪财经', 'https://finance.sina.com.cn/')
        
        # 新浪财经的新闻列表页
        self.news_list_urls = [
            'https://finance.sina.com.cn/roll/index.d.html?cid=56592',  # 财经要闻
            'https://finance.sina.com.cn/roll/index.d.html?cid=57526',  # 国内财经
            'https://finance.sina.com.cn/roll/index.d.html?cid=57592',  # 产经要闻
            'https://finance.sina.com.cn/roll/index.d.html?cid=56593',  # 证券要闻
            'https://finance.sina.com.cn/roll/index.d.html?cid=57495',  # 科技要闻
        ]
    
    def parse_news_list(self, html):
        """
        解析新闻列表页
        
        Args:
            html (str): HTML内容
            
        Returns:
            list: 新闻列表，每个元素为一个字典，包含标题、URL等信息
        """
        news_list = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找新闻列表
        news_items = soup.select('.list_009 li')
        
        for item in news_items:
            try:
                # 提取标题和URL
                a_tag = item.find('a')
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                url = a_tag['href']
                
                # 提取时间
                time_span = item.find('span')
                if not time_span:
                    continue
                
                time_str = time_span.text.strip()
                
                # 判断是否是今天的新闻
                if not self.is_recent(time_str, '%H:%M'):
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
            dict: 新闻详情，包含正文、发布时间等信息
        """
        html = self.get_html(url)
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # 提取正文
            article = soup.select_one('.article')
            if not article:
                article = soup.select_one('#artibody')
            
            if not article:
                return {}
            
            # 移除不需要的元素
            for tag in article.select('.img_descr, .article-video, script, style'):
                tag.decompose()
            
            content = article.get_text(strip=True)
            
            # 提取发布时间
            time_element = soup.select_one('.date')
            if time_element:
                publish_time = time_element.text.strip()
            else:
                publish_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
            
            # 提取作者
            author_element = soup.select_one('.author')
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
        抓取新浪财经新闻
        
        Args:
            hours (int, optional): 抓取最近多少小时的新闻
            
        Returns:
            list: 新闻列表，每个元素为一个字典，包含标题、URL、正文等信息
        """
        self.logger.info(f"开始抓取新浪财经新闻，最近{hours}小时")
        
        all_news = []
        
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
        
        self.logger.info(f"共抓取到 {len(all_news)} 条新浪财经新闻")
        return all_news 