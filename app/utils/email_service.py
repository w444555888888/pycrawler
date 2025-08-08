import smtplib  # Python 內建的 SMTP（發送郵件）模組
from email.mime.text import MIMEText  # 處理純文字格式郵件內容
from email.mime.multipart import MIMEMultipart  # 處理多段郵件（主旨、內文等）
import os


# env
EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


async def send_reset_email(to_email: str, token: str):
    subject = "重置密碼請求"
    reset_link = f"http://localhost:3000/reset-password/{token}"
    body = f"""請點擊以下鏈接重置你的密碼：
    {reset_link}
    如果你沒有請求此操作，請忽略此郵件。
    """

    # 建立一個多段郵件物件（含標題、內容）
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    # 將內文（純文字）加入郵件內容
    msg.attach(MIMEText(body, "plain"))

    try:
        # 建立與 Gmail SMTP 伺服器的連線，使用 TLS 加密（587 為 TLS port）
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"郵件發送失敗: {str(e)}")
