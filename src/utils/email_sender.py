import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from src.config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENTS, SMTP_SERVER, SMTP_PORT
from src.utils.logger import setup_logger

logger = setup_logger('email_sender')

def send_email(subject, html_content, recipients=None, attachments=None):
    """
    发送HTML格式的邮件
    
    Args:
        subject (str): 邮件主题
        html_content (str): HTML格式的邮件内容
        recipients (list, optional): 收件人列表，默认为配置中的收件人
        attachments (list, optional): 附件列表，每个元素为(文件名, 文件路径)
        
    Returns:
        bool: 是否发送成功
    """
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        logger.error("邮件发送失败：未配置发件人邮箱或密码")
        return False
    
    if recipients is None:
        recipients = EMAIL_RECIPIENTS
    
    if not recipients:
        logger.error("邮件发送失败：未指定收件人")
        return False
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # 添加HTML内容
        msg.attach(MIMEText(html_content, 'html'))
        
        # 添加附件
        if attachments:
            for attachment_name, attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                        msg.attach(attachment)
                else:
                    logger.warning(f"附件不存在：{attachment_path}")
        
        # 连接SMTP服务器并发送邮件
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"邮件发送成功：{subject}")
        return True
    
    except Exception as e:
        logger.error(f"邮件发送失败：{str(e)}")
        return False 