# 财经新闻聚合器 (Financial News Aggregator)

这个项目每天自动收集、分析和总结过去 24 小时内的重要财经新闻和政策信息，特别关注科技和金融行业的动态。

## 功能特点

- 自动抓取多个财经新闻源的最新信息
- 识别并提取重要的财经新闻和政策变化
- 特别关注科技和金融行业的动态
- 标注信息来源和相关上市公司的股票代码
- 对重大政策变化进行简要分析，评估其可能对市场的影响
- 生成每日财经新闻摘要报告
- 支持通过邮件发送每日报告

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/financial_news_aggregator.git
cd financial_news_aggregator
```

2. 安装依赖：

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

3. 配置环境变量：
   创建一个`.env`文件，包含以下内容：

```
# 邮件配置
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# 新闻API密钥（如果使用）
NEWS_API_KEY=your_api_key
```

## 使用方法

### 运行每日新闻收集和报告生成

```bash
python3 src/main.py
```

### 设置定时任务

可以使用 cron 作业每天自动运行：

```bash
# 每天早上7点运行
0 7 * * * cd /path/to/financial_news_aggregator && python3 src/main.py
```

### 启动 Web 界面（可选）

```bash
python3 src/web_app.py
```

然后在浏览器中访问 http://localhost:8000

## 项目结构

```
financial_news_aggregator/
├── data/                  # 存储抓取的新闻数据
├── logs/                  # 日志文件
├── src/
│   ├── scrapers/          # 新闻抓取模块
│   ├── processors/        # 新闻处理和分析模块
│   ├── reports/           # 报告生成模块
│   ├── storage/           # 数据存储模块
│   ├── utils/             # 工具函数
│   ├── main.py            # 主程序入口
│   └── web_app.py         # Web界面（可选）
└── requirements.txt       # 项目依赖
```

## 支持的新闻源

- 新浪财经
- 东方财富
- 华尔街见闻
- 彭博社
- 路透社
- 财新网
- 第一财经
- 界面新闻
- 中国证券报
- 证券时报

## 贡献

欢迎提交问题和拉取请求！

## 许可证

MIT
