import asyncio
import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from openai import OpenAI

# ================== 配置（从Railway环境变量读取）==================
YOUR_EMAIL = "3069034724@qq.com"
EMAIL_PASS = os.getenv("EMAIL_PASS")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not EMAIL_PASS or not DEEPSEEK_API_KEY:
    raise ValueError("缺少环境变量！请在Railway设置 EMAIL_PASS 和 DEEPSEEK_API_KEY")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

RSS_FEEDS = [
    "https://rsshub.app/cls/telegraph",
    "http://rss.sina.com.cn/finance/fund.xml",
    "http://rss.sina.com.cn/finance/financial.xml",
    "https://rsshub.app/eastmoney/report/宏观研究",
    "https://rsshub.app/eastmoney/report/策略报告",
    "https://rsshub.app/wallstreetcn/news",
    "https://rsshub.app/21caijing/flash",
    "https://rsshub.app/yicai/brief",
]

def fetch_rss_feeds():
    all_content = f"📅 {datetime.now().strftime('%Y-%m-%d')} 基金·金融·宏观·政策每日精选\n\n"
    for rss_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(rss_url)
            source_title = getattr(feed.feed, 'title', rss_url)
            all_content += f"🔹 来源：{source_title}\n"
            for entry in feed.entries[:6]:
                title = entry.title
                desc = getattr(entry, 'description', '')[:200]
                all_content += f"• {title}\n"
                if desc:
                    all_content += f"  {desc}...\n"
            all_content += "\n"
        except:
            all_content += f"⚠️ 获取失败: {rss_url}\n\n"
    return all_content

def deepseek_summary(content):
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是一位资深的中国宏观经济与金融分析师。用简洁、专业、有洞察力的中文总结，重点突出基金动态、金融市场、政策信号和国家长期发展趋势。分���列出，最后加1-2句趋势判断。"},
            {"role": "user", "content": content}
        ],
        temperature=0.6,
        max_tokens=1500
    )
    return response.choices[0].message.content

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(YOUR_EMAIL, EMAIL_PASS)
    server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())
    server.quit()
    print("✅ 邮件发送成功")

async def main():
    print("🚀 开始每日任务...")
    raw = fetch_rss_feeds()
    print("🤖 DeepSeek AI总结中...")
    summary = deepseek_summary(raw)
    subject = f"每日基金·金融·宏观 AI总结 {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, summary)
    print("✅ 全部完成！")

if __name__ == "__main__":
    asyncio.run(main())
