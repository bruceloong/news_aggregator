import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

from src.config import LOG_LEVEL, LOG_FORMAT, LOG_DIR

def setup_logger(name):
    """
    设置并返回一个命名的日志记录器
    
    Args:
        name: 日志记录器的名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    log_file = os.path.join(LOG_DIR, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger 