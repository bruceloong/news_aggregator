#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import random
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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
        
        # 添加热门新闻页面
        self.hot_news_url = 'https://finance.eastmoney.com/'
    
    def get_html(self, url, params=None, retries=3):
        """
        重写父类的get_html方法，指定编码为utf-8
        
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
                # 明确指定编码为utf-8
                response.encoding = 'utf-8'
                return response.text
            except Exception as e:
                self.logger.error(f"获取HTML失败 ({i+1}/{retries}): {url}, 错误: {str(e)}")
                if i < retries - 1:
                    # 随机等待1-3秒后重试
                    time.sleep(random.uniform(1, 3))
        return ""
    
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
        
        # 网站结构已变化，更新选择器
        # 尝试从"网友点击排行榜"中获取新闻
        news_items = soup.select('.Wydj .tabList li')
        
        for item in news_items:
            try:
                # 提取标题和URL
                a_tag = item.find('a')
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                url = a_tag['href']
                
                # 由于排行榜没有明确的时间，我们假设它们是最近的新闻
                news_list.append({
                    'title': title,
                    'url': url,
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': self.source_name
                })
            except Exception as e:
                self.logger.error(f"解析新闻项失败: {str(e)}")
        
        # 尝试从"资讯精华"中获取新闻
        news_items = soup.select('.Ywjh .artitleList li')
        
        for item in news_items:
            try:
                # 提取标题和URL
                a_tag = item.select_one('.title a')
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                url = a_tag['href']
                
                # 由于资讯精华没有明确的时间，我们假设它们是最近的新闻
                news_list.append({
                    'title': title,
                    'url': url,
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': self.source_name
                })
            except Exception as e:
                self.logger.error(f"解析新闻项失败: {str(e)}")
        
        # 尝试从"评论精华"中获取新闻
        news_items = soup.select('.Pljh .artitleList li')
        
        for item in news_items:
            try:
                # 提取标题和URL
                a_tag = item.select_one('.title a')
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                url = a_tag['href']
                
                # 由于评论精华没有明确的时间，我们假设它们是最近的新闻
                news_list.append({
                    'title': title,
                    'url': url,
                    'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': self.source_name
                })
            except Exception as e:
                self.logger.error(f"解析新闻项失败: {str(e)}")
        
        return news_list
    
    def parse_hot_news(self):
        """
        解析东方财富首页的热门新闻
        
        Returns:
            list: 新闻列表
        """
        news_list = []
        
        try:
            html = self.get_html(self.hot_news_url)
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试获取首页的热门新闻
            news_items = soup.select('.news-hot-list li, .news-list li')
            
            for item in news_items:
                try:
                    # 提取标题和URL
                    a_tag = item.find('a')
                    if not a_tag:
                        continue
                    
                    title = a_tag.text.strip()
                    url = a_tag['href']
                    
                    # 由于热门新闻没有明确的时间，我们假设它们是最近的新闻
                    news_list.append({
                        'title': title,
                        'url': url,
                        'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': self.source_name
                    })
                except Exception as e:
                    self.logger.error(f"解析热门新闻项失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"解析热门新闻失败: {str(e)}")
        
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
            article = soup.select_one('.article-content, .newsContent, #ContentBody')
            
            if not article:
                return {}
            
            # 移除不需要的元素
            for tag in article.select('.em_media_box'):
                tag.decompose()
            
            content = article.get_text(strip=True)
            
            # 提取发布时间
            time_element = soup.select_one('.time, .time-source, .article-meta span')
            publish_time = ''
            if time_element:
                publish_time = time_element.get_text(strip=True)
                # 尝试提取时间部分
                time_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}', publish_time)
                if time_match:
                    publish_time = time_match.group()
            
            # 提取来源
            source_element = soup.select_one('.source, .data-source')
            source = ''
            if source_element:
                source = source_element.get_text(strip=True)
                # 尝试提取来源部分
                source_match = re.search(r'来源：(.*)', source)
                if source_match:
                    source = source_match.group(1)
            
            return {
                'content': content,
                'publish_time': publish_time if publish_time else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_detail': source
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
        
        # 抓取热门新闻
        hot_news = self.parse_hot_news()
        self.logger.info(f"从首页抓取到 {len(hot_news)} 条热门新闻")
        all_news.extend(hot_news)
        
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
        
        # 去重
        unique_news = []
        urls = set()
        for news in all_news:
            if news['url'] not in urls:
                urls.add(news['url'])
                unique_news.append(news)
        
        self.logger.info(f"共抓取到 {len(unique_news)} 条东方财富新闻")
        return unique_news 