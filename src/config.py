#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志配置
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 数据存储配置
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
RAW_NEWS_DIR = os.path.join(DATA_DIR, 'raw_news')
os.makedirs(RAW_NEWS_DIR, exist_ok=True)
PROCESSED_NEWS_DIR = os.path.join(DATA_DIR, 'processed_news')
os.makedirs(PROCESSED_NEWS_DIR, exist_ok=True)
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# 邮件配置
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(',')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# 新闻源配置
NEWS_SOURCES = {
    'sina': {
        'name': '新浪财经',
        'url': 'https://finance.sina.com.cn/',
        'enabled': True
    },
    'eastmoney': {
        'name': '东方财富',
        'url': 'https://www.eastmoney.com/',
        'enabled': True
    },
    'wallstreetcn': {
        'name': '华尔街见闻',
        'url': 'https://wallstreetcn.com/',
        'enabled': True
    },
    'bloomberg': {
        'name': '彭博社',
        'url': 'https://www.bloomberg.com/',
        'enabled': True
    },
    'reuters': {
        'name': '路透社',
        'url': 'https://www.reuters.com/',
        'enabled': True
    },
    'caixin': {
        'name': '财新网',
        'url': 'https://www.caixin.com/',
        'enabled': True
    },
    'yicai': {
        'name': '第一财经',
        'url': 'https://www.yicai.com/',
        'enabled': True
    },
    'jiemian': {
        'name': '界面新闻',
        'url': 'https://www.jiemian.com/',
        'enabled': True
    },
    'cs': {
        'name': '中国证券报',
        'url': 'https://www.cs.com.cn/',
        'enabled': True
    },
    'stcn': {
        'name': '证券时报',
        'url': 'https://www.stcn.com/',
        'enabled': True
    }
}

# 关注的行业
FOCUS_INDUSTRIES = ['科技', '金融', '互联网', '人工智能', '半导体', '新能源', '医药', '房地产']

# 关键词配置
POLICY_KEYWORDS = ['政策', '监管', '法规', '规定', '条例', '措施', '通知', '决定', 
                  '央行', '证监会', '银保监会', '发改委', '财政部', '税务总局']

IMPORTANT_KEYWORDS = ['重大', '突破', '首次', '创新', '重要', '关键', '战略', '突发',
                     '紧急', '危机', '风险', '机遇', '挑战', '转折', '里程碑']

# Web应用配置
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', 8000))

# 报告配置
REPORT_TEMPLATE = os.path.join(os.path.dirname(__file__), 'reports', 'templates', 'daily_report.html') 