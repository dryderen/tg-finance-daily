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

print(f"[DEBUG] EMAIL_PASS 设置: {bool(EMAIL_PASS)}")
print(f"[DEBUG] DEEPSEEK_API_KEY 设置: {bool(DEEPSEEK_API_KEY)}")

if not EMAIL_PASS or not DEEPSEEK_API_KEY:
    print("❌ 缺少环境变量！")
    print(f"  EMAIL_PASS: {'✓ 已设置' if EMAIL_PASS else '✗ 未设置'}")
    print(f"  DEEPSEEK_API_KEY: {'✓ 已设置' if DEEPSEEK_API_KEY else '✗ 未设置'}")
    exit(1)

print("✅ 环境变量检查通过")

try:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    print("✅ DeepSeek 客户端初始化成功")
except Exception as e:
    print(f"❌ DeepSeek 初始化失败: {e}")
    exit(1)

# RSS 来源
RSS_FEEDS = [
    "https://rsshub.app/cls/telegraph",
    "http://rss.sina.com.cn/finance/fund.xml",
    "https://rsshub.app/wallstreetcn/news",
    "https://rsshub.app/eastmoney/report/宏观研究",
]

def fetch_news():
    print("📰 开始抓取新闻...")
    content = f"📅 {datetime.now().strftime('%Y-%m-%d')} 基金·金融·宏观每日摘要\n\n"
    for url in RSS_FEEDS:
        try:
            print(f"  抓取: {url}")
            feed = feedparser.parse(url)
            source = getattr(feed.feed, 'title', url)
            content += f"🔹 来源：{source}\n"
            for entry in feed.entries[:5]:
                content += f"• {entry.title}\n"
            content += "\n"
        except Exception as e:
            print(f"  ⚠️ 获取失败: {url} - {str(e)}")
            content += f"⚠️ {url} 获取失败\n\n"
    print("✅ 新闻抓取完成")
    return content

def ai_summary(text):
    print("🤖 AI 总结中...")
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "你是专业的金融���析师，用简洁中文分点总结重点，突出政策和趋势。"},
                {"role": "user", "content": text}
            ],
            max_tokens=1000
        )
        summary = response.choices[0].message.content
        print("✅ AI 总结完成")
        return summary
    except Exception as e:
        print(f"❌ AI 总结失败: {e}")
        raise

def send_email(body):
    print("📧 发送邮件中...")
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(f"每日金融宏观 AI总结 {datetime.now().strftime('%Y-%m-%d')}", "utf-8")
        msg["From"] = YOUR_EMAIL
        msg["To"] = YOUR_EMAIL

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(YOUR_EMAIL, EMAIL_PASS)
        server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        raise

async def run():
    try:
        print("🚀 开始任务...")
        news = fetch_news()
        summary = ai_summary(news)
        send_email(summary)
        print("🎉 今日任务完成！")
        return 0
    except Exception as e:
        print(f"❌ 任务失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run())
    exit(exit_code)
