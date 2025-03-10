#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import schedule
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.logger import setup_logger
from src.utils.email_sender import send_email
from src.scrapers import get_all_scrapers
from src.processors.news_processor import NewsProcessor
from src.reports.report_generator import ReportGenerator
from src.storage.news_storage import NewsStorage
from src.config import NEWS_SOURCES, EMAIL_RECIPIENTS

logger = setup_logger('main')

def scrape_news():
    """
    抓取新闻
    
    Returns:
        list: 所有抓取到的新闻
    """
    logger.info("开始抓取新闻")
    
    all_news = []
    storage = NewsStorage()
    
    # 获取所有爬虫
    scrapers = get_all_scrapers()
    
    # 抓取新闻
    for scraper in scrapers:
        try:
            source_id = scraper.source_id
            source_config = NEWS_SOURCES.get(source_id, {})
            
            # 检查是否启用
            if not source_config.get('enabled', True):
                logger.info(f"跳过已禁用的新闻源: {scraper.source_name}")
                continue
            
            logger.info(f"开始抓取新闻源: {scraper.source_name}")
            
            # 抓取新闻
            news_list = scraper.scrape()
            
            # 保存原始新闻
            if news_list:
                storage.save_raw_news(news_list, source_id)
                all_news.extend(news_list)
                logger.info(f"从 {scraper.source_name} 抓取到 {len(news_list)} 条新闻")
            else:
                logger.warning(f"从 {scraper.source_name} 没有抓取到新闻")
        
        except Exception as e:
            logger.error(f"抓取新闻源 {scraper.source_name} 失败: {str(e)}")
    
    logger.info(f"共抓取到 {len(all_news)} 条新闻")
    return all_news

def process_news(news_list):
    """
    处理新闻
    
    Args:
        news_list (list): 新闻列表
        
    Returns:
        list: 处理后的新闻列表
    """
    logger.info("开始处理新闻")
    
    processor = NewsProcessor()
    storage = NewsStorage()
    
    # 处理新闻
    processed_news = processor.process_news(news_list)
    
    # 保存处理后的新闻
    if processed_news:
        storage.save_processed_news(processed_news)
        logger.info(f"处理了 {len(processed_news)} 条新闻")
    else:
        logger.warning("没有处理到任何新闻")
    
    return processed_news

def generate_report(news_list):
    """
    生成报告
    
    Args:
        news_list (list): 新闻列表
        
    Returns:
        tuple: (报告HTML内容, 报告文件路径)
    """
    logger.info("开始生成报告")
    
    generator = ReportGenerator()
    
    # 生成报告
    report_date = datetime.now()
    html_content = generator.generate_daily_report(news_list, report_date)
    
    # 保存报告
    report_path = generator.save_report(html_content, report_date)
    
    logger.info(f"报告已生成: {report_path}")
    
    return html_content, report_path

def send_report_email(html_content, report_path):
    """
    发送报告邮件
    
    Args:
        html_content (str): 报告HTML内容
        report_path (str): 报告文件路径
        
    Returns:
        bool: 是否发送成功
    """
    logger.info("开始发送报告邮件")
    
    # 创建邮件主题
    subject = f"每日财经新闻摘要 - {datetime.now().strftime('%Y年%m月%d日')}"
    
    # 创建附件
    attachments = [
        (os.path.basename(report_path), report_path)
    ]
    
    # 发送邮件
    success = send_email(subject, html_content, EMAIL_RECIPIENTS, attachments)
    
    if success:
        logger.info("报告邮件发送成功")
    else:
        logger.error("报告邮件发送失败")
    
    return success

def run_daily_task():
    """
    运行每日任务
    """
    logger.info("开始运行每日任务")
    
    try:
        # 抓取新闻
        news_list = scrape_news()
        
        if not news_list:
            logger.warning("没有抓取到任何新闻，任务结束")
            return
        
        # 处理新闻
        processed_news = process_news(news_list)
        
        if not processed_news:
            logger.warning("没有处理到任何新闻，任务结束")
            return
        
        # 生成报告
        html_content, report_path = generate_report(processed_news)
        
        # 发送报告邮件
        send_report_email(html_content, report_path)
        
        logger.info("每日任务完成")
    
    except Exception as e:
        logger.error(f"运行每日任务失败: {str(e)}")

def schedule_tasks():
    """
    调度任务
    """
    logger.info("开始调度任务")
    
    # 每天早上7点运行
    schedule.every().day.at("07:00").do(run_daily_task)
    
    logger.info("任务已调度，等待执行")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logger.info("财经新闻聚合器启动")
    
    # 如果有命令行参数，直接运行任务
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_daily_task()
    else:
        # 否则调度任务
        schedule_tasks() 