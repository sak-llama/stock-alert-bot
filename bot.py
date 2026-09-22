import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import yfinance as yf

# ดึงค่าจาก GitHub Secrets
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# อีเมลผู้รับ (อาจจะเป็นเมลเดียวกับผู้ส่ง)

WATCH_LIST = ["NVDA", "AAPL", "GOOGL"]
DROP_THRESHOLD = 5.0


def send_email_notification(subject, message):
  if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
    print("Error: ข้อมูลอีเมลไม่ครบถ้วนใน Environment Variables")
    return

  try:
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    # เชื่อมต่อ SMTP Server ของ Gmail
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
    server.quit()
    print("ส่งอีเมลแจ้งเตือนสำเร็จ!")
  except Exception as e:
    print(f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}")


def check_stock_prices():
  print(
      f"กำลังตรวจสอบราคาและข่าว (เกณฑ์แจ้งเตือน: ร่วงมากกว่าหรือเท่ากับ"
      f" {DROP_THRESHOLD}%)..."
  )
  for ticker in WATCH_LIST:
    try:
      stock = yf.Ticker(ticker)
      df = stock.history(period="2d")
      if len(df) >= 2:
        prev_close = df["Close"].iloc[-2]
        current_price = df["Close"].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        print(f"{ticker}: ราคาปัจจุบัน {current_price:.2f} ({change_pct:.2f}%)")

        if change_pct <= -abs(DROP_THRESHOLD):
          news_list = stock.news
          news_headlines = ""
          if news_list:
            headlines = [
                item.get("title", "ไม่มีหัวข้อข่าว") for item in news_list[:2]
            ]
            news_headlines = "\n".join([f"- {h}" for h in headlines])
          else:
            news_headlines = "- ไม่พบข่าวอัปเดตในช่วงนี้"

          subject = f"⚠️ แจ้งเตือนด่วน: หุ้น {ticker} ดิ่ง {change_pct:.2f}%!"
          msg = (
              f"ชื่อหุ้น: {ticker}\nร่วงไป: {change_pct:.2f}%\nราคาปัจจุบัน:"
              f" ${current_price:.2f}\n\n📰 ข่าวล่าสุด:\n{news_headlines}"
          )
          send_email_notification(subject, msg)
    except Exception as e:
      print(f"เกิดข้อผิดพลาดสำหรับ {ticker}: {e}")


if __name__ == "__main__":
  check_stock_prices()
 
