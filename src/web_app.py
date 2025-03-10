#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.logger import setup_logger
from src.storage.news_storage import NewsStorage
from src.processors.news_processor import NewsProcessor
from src.reports.report_generator import ReportGenerator
from src.config import REPORTS_DIR, WEB_HOST, WEB_PORT

# 创建FastAPI应用
app = FastAPI(title="财经新闻聚合器", description="每日财经新闻摘要")

# 创建日志记录器
logger = setup_logger('web_app')

# 创建静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)

# 创建模板目录
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
os.makedirs(templates_dir, exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 创建模板引擎
templates = Jinja2Templates(directory=templates_dir)

# 创建首页模板
index_template_path = os.path.join(templates_dir, 'index.html')
if not os.path.exists(index_template_path):
    with open(index_template_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财经新闻聚合器</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>财经新闻聚合器</h1>
    </header>
    
    <main>
        <section class="reports">
            <h2>最新报告</h2>
            <ul>
                {% for report in reports %}
                <li>
                    <a href="/report/{{ report.filename }}">{{ report.date }}</a>
                </li>
                {% endfor %}
            </ul>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2023 财经新闻聚合器</p>
    </footer>
</body>
</html>""")

# 创建CSS样式文件
css_file_path = os.path.join(static_dir, 'style.css')
if not os.path.exists(css_file_path):
    with open(css_file_path, 'w', encoding='utf-8') as f:
        f.write("""body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

h2 {
    color: #2c3e50;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-top: 30px;
}

.reports ul {
    list-style: none;
    padding: 0;
}

.reports li {
    margin-bottom: 10px;
    padding: 10px;
    background-color: #f9f9f9;
    border-left: 4px solid #3498db;
    border-radius: 0 5px 5px 0;
}

.reports a {
    text-decoration: none;
    color: #3498db;
    font-weight: bold;
}

.reports a:hover {
    text-decoration: underline;
}

footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    color: #7f8c8d;
    font-size: 14px;
}""")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    首页，显示所有报告列表
    """
    # 获取所有报告文件
    reports = []
    
    if os.path.exists(REPORTS_DIR):
        for filename in os.listdir(REPORTS_DIR):
            if filename.startswith('daily_report_') and filename.endswith('.html'):
                # 从文件名中提取日期
                date_str = filename.replace('daily_report_', '').replace('.html', '')
                try:
                    date = datetime.strptime(date_str, '%Y%m%d')
                    reports.append({
                        'filename': filename,
                        'date': date.strftime('%Y年%m月%d日')
                    })
                except:
                    pass
    
    # 按日期排序
    reports.sort(key=lambda x: x['filename'], reverse=True)
    
    return templates.TemplateResponse("index.html", {"request": request, "reports": reports})

@app.get("/report/{filename}", response_class=HTMLResponse)
async def read_report(filename: str):
    """
    查看指定的报告
    """
    report_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return FileResponse(report_path)

@app.get("/generate", response_class=HTMLResponse)
async def generate_new_report(request: Request):
    """
    生成新的报告
    """
    try:
        # 获取最新的处理后的新闻
        storage = NewsStorage()
        news_list = storage.get_latest_processed_news()
        
        if not news_list:
            return {"message": "没有找到处理后的新闻数据"}
        
        # 生成报告
        generator = ReportGenerator()
        report_date = datetime.now()
        html_content = generator.generate_daily_report(news_list, report_date)
        report_path = generator.save_report(html_content, report_date)
        
        # 重定向到报告页面
        filename = os.path.basename(report_path)
        return {"message": "报告生成成功", "report_url": f"/report/{filename}"}
    
    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")

def start():
    """
    启动Web应用
    """
    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT)

if __name__ == "__main__":
    start() 