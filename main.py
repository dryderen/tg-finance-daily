import asyncio
import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from openai import OpenAI

# 配置
YOUR_EMAIL = "3069034724@qq.com"
EMAIL_PASS = os.getenv("EMAIL_PASS")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not EMAIL_PASS or not DEEPSEEK_API_KEY:
    print("❌ 缺少环境变量，请在 Railway 设置")
    exit(1)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# RSS 来源（基金、金融、宏观）
RSS_FEEDS = [
    "https://rsshub.app/cls/telegraph",
    "http://rss.sina.com.cn/finance/fund.xml",
    "https://rsshub.app/wallstreetcn/news",
    "https://rsshub.app/eastmoney/report/宏观研究",
]

def fetch_news():
    content = f"📅 {datetime.now().strftime('%Y-%m-%d')} 基金·金融·宏观每日摘要\n\n"
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source = getattr(feed.feed, 'title', url)
            content += f"🔹 来源：{source}\n"
            for entry in feed.entries[:5]:
                content += f"• {entry.title}\n"
            content += "\n"
        except:
            content += f"⚠️ {url} 获取失败\n\n"
    return content

def ai_summary(text):
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是专业的金融分析师，用简洁中文分点总结重点，突出政策和趋势。"},
            {"role": "user", "content": text}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

def send_email(body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(f"每日金融宏观 AI总结 {datetime.now().strftime('%Y-%m-%d')}", "utf-8")
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(YOUR_EMAIL, EMAIL_PASS)
    server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())
    server.quit()
    print("✅ 邮件发送成功！")

async def run():
    print("🚀 开始抓取新闻...")
    news = fetch_news()
    print("🤖 AI 总结中...")
    summary = ai_summary(news)
    print("📧 发送邮件中...")
    send_email(summary)
    print("🎉 今日任务完成")

if __name__ == "__main__":
    asyncio.run(run())
