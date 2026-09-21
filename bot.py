import os
import requests
import yfinance as yf

LINE_TOKEN = os.environ.get("LINE_TOKEN")
WATCH_LIST = ["NVDA", "AAPL", "GOOGL"]
DROP_THRESHOLD = 5.0


def send_line_notify(message):
  if not LINE_TOKEN:
    print("Error: ไม่พบ LINE_TOKEN")
    return
  url = "https://notify-api.line.me/api/notify"
  headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
  data = {"message": message}
  requests.post(url, headers=headers, data=data)


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

          msg = (
              f"\n⚠️ แจ้งเตือนหุ้น/กองทุนดิ่งเกินเป้า!\nชื่อ: {ticker}\nร่วงไป:"
              f" {change_pct:.2f}%\nราคาปัจจุบัน: ${current_price:.2f}\n\n📰"
              f" ข่าวล่าสุดที่เกี่ยวข้อง:\n{news_headlines}"
          )
          send_line_notify(msg)
    except Exception as e:
      print(f"เกิดข้อผิดพลาดสำหรับ {ticker}: {e}")


if __name__ == "__main__":
  check_stock_prices()
