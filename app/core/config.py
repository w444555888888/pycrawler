# 載入 python-dotenv 模組，用來從 .env 檔案讀取環境變數
from dotenv import load_dotenv
# os 模組用來操作環境變數、路徑等
import os

# 執行 dotenv 載入，會自動從專案根目錄的 `.env` 檔案讀取變數並注入到環境變數中
load_dotenv()
class Settings:
    # 從環境變數中取得 MONGODB 的設定值，若未設定則使用預設值 "mongodb://localhost:27017/default"
    MONGODB_URI = os.getenv("MONGODB", "mongodb://localhost:27017/default")

# 建立設定實例供其他模組匯入使用
settings = Settings()
