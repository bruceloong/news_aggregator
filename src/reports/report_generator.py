import os
import json
from datetime import datetime
import jinja2

from src.utils.logger import setup_logger
from src.config import REPORTS_DIR

logger = setup_logger('report_generator')

class ReportGenerator:
    """
    报告生成器，用于生成新闻摘要报告
    """
    
    def __init__(self):
        """
        初始化报告生成器
        """
        self.logger = logger
        
        # 创建Jinja2环境
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate_daily_report(self, news_data, report_date=None):
        """
        生成每日新闻摘要报告
        
        Args:
            news_data (list): 新闻数据
            report_date (datetime, optional): 报告日期，默认为当前日期
            
        Returns:
            str: 报告HTML内容
        """
        if report_date is None:
            report_date = datetime.now()
        
        # 按类型分组新闻
        news_by_type = {}
        for news in news_data:
            news_type = news.get('news_type', '一般新闻')
            if news_type not in news_by_type:
                news_by_type[news_type] = []
            news_by_type[news_type].append(news)
        
        # 按行业分组新闻
        news_by_industry = {}
        for news in news_data:
            related_industries = news.get('related_industries', [])
            if not related_industries:
                if '其他' not in news_by_industry:
                    news_by_industry['其他'] = []
                news_by_industry['其他'].append(news)
                continue
            
            for industry in related_industries:
                if industry not in news_by_industry:
                    news_by_industry[industry] = []
                news_by_industry[industry].append(news)
        
        # 提取政策新闻
        policy_news = [news for news in news_data if news.get('policy_info', False)]
        
        # 提取重要新闻
        important_news = [news for news in news_data if news.get('important', False)]
        
        # 渲染模板
        try:
            template = self.jinja_env.get_template('daily_report.html')
            html_content = template.render(
                report_date=report_date.strftime('%Y年%m月%d日'),
                news_count=len(news_data),
                news_by_type=news_by_type,
                news_by_industry=news_by_industry,
                policy_news=policy_news,
                important_news=important_news
            )
            return html_content
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            # 如果模板不存在，创建一个默认模板
            self._create_default_template()
            return self._generate_default_report(news_data, report_date)
    
    def _create_default_template(self):
        """
        创建默认的报告模板
        """
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'daily_report.html')
        
        if os.path.exists(template_path):
            return
        
        template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日财经新闻摘要 - {{ report_date }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        h1 {
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        .news-item {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            border-radius: 0 5px 5px 0;
        }
        .news-title {
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .news-source {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .news-content {
            margin-bottom: 10px;
        }
        .news-meta {
            font-size: 14px;
            color: #7f8c8d;
        }
        .stock-code {
            background-color: #e74c3c;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 5px;
            font-size: 12px;
        }
        .policy-news {
            border-left-color: #e74c3c;
        }
        .important-news {
            border-left-color: #f39c12;
        }
        .industry-news {
            border-left-color: #2ecc71;
        }
        .summary-section {
            margin-bottom: 30px;
        }
        .summary-count {
            font-weight: bold;
            color: #3498db;
        }
        .keywords {
            margin-top: 10px;
        }
        .keyword {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 15px;
            margin-right: 5px;
            margin-bottom: 5px;
            font-size: 12px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>每日财经新闻摘要 - {{ report_date }}</h1>
    
    <div class="summary-section">
        <h2>摘要</h2>
        <p>今日共收集了 <span class="summary-count">{{ news_count }}</span> 条财经新闻。</p>
    </div>
    
    {% if policy_news %}
    <div class="summary-section">
        <h2>政策信息</h2>
        {% for news in policy_news %}
        <div class="news-item policy-news">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-source">来源: {{ news.source }} | 发布时间: {{ news.publish_time }}</div>
            <div class="news-content">{{ news.content[:200] }}{% if news.content|length > 200 %}...{% endif %}</div>
            <div class="news-meta">
                {% if news.stock_codes %}
                <div>相关公司及股票代码: 
                    {% for company, code in news.stock_codes.items() %}
                    <span>{{ company }} <span class="stock-code">{{ code }}</span></span>
                    {% endfor %}
                </div>
                {% endif %}
                {% if news.keywords %}
                <div class="keywords">
                    {% for keyword in news.keywords %}
                    <span class="keyword">{{ keyword }}</span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if news_by_industry %}
    <div class="summary-section">
        <h2>行业动态</h2>
        {% for industry, industry_news in news_by_industry.items() %}
        <h3>{{ industry }}</h3>
        {% for news in industry_news %}
        <div class="news-item industry-news">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-source">来源: {{ news.source }} | 发布时间: {{ news.publish_time }}</div>
            <div class="news-content">{{ news.content[:200] }}{% if news.content|length > 200 %}...{% endif %}</div>
            <div class="news-meta">
                {% if news.stock_codes %}
                <div>相关公司及股票代码: 
                    {% for company, code in news.stock_codes.items() %}
                    <span>{{ company }} <span class="stock-code">{{ code }}</span></span>
                    {% endfor %}
                </div>
                {% endif %}
                {% if news.keywords %}
                <div class="keywords">
                    {% for keyword in news.keywords %}
                    <span class="keyword">{{ keyword }}</span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
        {% endfor %}
    </div>
    {% endif %}
    
    {% if important_news %}
    <div class="summary-section">
        <h2>重要新闻</h2>
        {% for news in important_news %}
        <div class="news-item important-news">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-source">来源: {{ news.source }} | 发布时间: {{ news.publish_time }}</div>
            <div class="news-content">{{ news.content[:200] }}{% if news.content|length > 200 %}...{% endif %}</div>
            <div class="news-meta">
                {% if news.stock_codes %}
                <div>相关公司及股票代码: 
                    {% for company, code in news.stock_codes.items() %}
                    <span>{{ company }} <span class="stock-code">{{ code }}</span></span>
                    {% endfor %}
                </div>
                {% endif %}
                {% if news.keywords %}
                <div class="keywords">
                    {% for keyword in news.keywords %}
                    <span class="keyword">{{ keyword }}</span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if news_by_type.get('一般新闻') %}
    <div class="summary-section">
        <h2>其他新闻</h2>
        {% for news in news_by_type.get('一般新闻') %}
        <div class="news-item">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-source">来源: {{ news.source }} | 发布时间: {{ news.publish_time }}</div>
            <div class="news-content">{{ news.content[:200] }}{% if news.content|length > 200 %}...{% endif %}</div>
            <div class="news-meta">
                {% if news.stock_codes %}
                <div>相关公司及股票代码: 
                    {% for company, code in news.stock_codes.items() %}
                    <span>{{ company }} <span class="stock-code">{{ code }}</span></span>
                    {% endfor %}
                </div>
                {% endif %}
                {% if news.keywords %}
                <div class="keywords">
                    {% for keyword in news.keywords %}
                    <span class="keyword">{{ keyword }}</span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="footer">
        <p>财经新闻聚合器 - 自动生成于 {{ report_date }} {{ now.strftime('%H:%M:%S') }}</p>
    </div>
</body>
</html>
"""
        
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.logger.info(f"已创建默认报告模板: {template_path}")
    
    def _generate_default_report(self, news_data, report_date):
        """
        生成默认的报告内容
        
        Args:
            news_data (list): 新闻数据
            report_date (datetime): 报告日期
            
        Returns:
            str: 报告HTML内容
        """
        # 创建一个简单的HTML报告
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <title>每日财经新闻摘要</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; line-height: 1.6; }',
            '        .news-item { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }',
            '        .news-title { font-weight: bold; }',
            '        .news-meta { color: #666; font-size: 0.9em; }',
            '    </style>',
            '</head>',
            '<body>',
            f'    <h1>每日财经新闻摘要 - {report_date.strftime("%Y年%m月%d日")}</h1>',
            f'    <p>今日共收集了 {len(news_data)} 条财经新闻。</p>'
        ]
        
        # 添加新闻内容
        for news in news_data:
            html_parts.extend([
                '    <div class="news-item">',
                f'        <div class="news-title">{news.get("title", "")}</div>',
                f'        <div class="news-meta">来源: {news.get("source", "")} | 发布时间: {news.get("publish_time", "")}</div>',
                f'        <div class="news-content">{news.get("content", "")[:200]}{"..." if len(news.get("content", "")) > 200 else ""}</div>',
                '    </div>'
            ])
        
        html_parts.extend([
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def save_report(self, html_content, report_date=None):
        """
        保存报告
        
        Args:
            html_content (str): 报告HTML内容
            report_date (datetime, optional): 报告日期，默认为当前日期
            
        Returns:
            str: 保存的文件路径
        """
        if report_date is None:
            report_date = datetime.now()
        
        # 创建文件名
        filename = f"daily_report_{report_date.strftime('%Y%m%d')}.html"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # 保存HTML文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"报告已保存到: {filepath}")
        return filepath 