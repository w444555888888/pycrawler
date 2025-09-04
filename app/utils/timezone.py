# utils/timezone.py
from __future__ import annotations  # 讓型別註解延後解析（前向參照更安全；本檔雖未用到，保留作為通用設定）
from typing import Optional, Tuple    # Optional[T] 表示可能是 T 或 None；Tuple[float, float] 用於 (lat, lng)
from functools import lru_cache       # LRU 快取裝飾器，避免重複查詢造成延遲或打爆外部服務
from geopy.geocoders import Nominatim # OSM 的地理編碼器：用地名換經緯度（需要網路，具速率限制）
from timezonefinder import TimezoneFinder  # 依經緯度推 IANA 時區（純本地計算、無網路）
import asyncio                         # 把同步 I/O 丟到執行緒池，避免阻塞事件迴圈



# 建立單例（全域共用，避免重複初始化）
# - user_agent 必填，遵守 Nominatim 使用規範
# - timeout 防止外部請求卡住太久
_geolocator = Nominatim(user_agent="boolingChallenge.flights (contact: w444555888@yahoo.com.tw)", timeout=5)
# TimezoneFinder 內部會載入時區邊界資料，實例化一次重複使用
_tf = TimezoneFinder()


@lru_cache(maxsize=1024)
def _coords_by_city_sync(city_name: str) -> Optional[Tuple[float, float]]:
    """
    同步版：由城市名稱取得 (latitude, longitude)。
    - 這是「同步 + 可快取」函式，本身會做網路 I/O，不要在事件迴圈中直接呼叫
    - 快取 1024 組輸入 → 輸出，可大幅降低對 Nominatim 的呼叫次數。
    回傳：
      - (lat, lng) 例如 (25.0375, 121.5637)
      - 查不到或發生錯誤時回 None
    """
    if not city_name:
        return None
    try:
        # exactly_one=True：若有多個同名城市，僅取第一筆（語意與 Node 版 city-timezones 取第一筆一致）
        loc = _geolocator.geocode(city_name, exactly_one=True)
        if not loc:
            return None
        return (loc.latitude, loc.longitude)
    except Exception as e:
        print(f"[get_coords_by_city] geocode error: {e}")
        return None

async def get_coords_by_city(city_name: str) -> Optional[Tuple[float, float]]:
    """
    非阻塞版：把同步 geocode 丟到預設執行緒池跑，避免阻塞 FastAPI 事件迴圈。

    # run_in_executor(executor, func, *args)
    return await loop.run_in_executor(
        None,                 # 第一個參數：executor
                              # None = 使用預設的 ThreadPoolExecutor（背景執行緒池）

        _coords_by_city_sync, # 第二個參數：func
                              # 要執行的同步函式（這裡就是 _coords_by_city_sync）

        city_name             # 第三個參數：*args
                              # 傳給 func 的參數，等於呼叫 _coords_by_city_sync(city_name)
    )

    回傳：
      - (lat, lng): Tuple[float, float]
        成功時回傳一個 tuple，包含經緯度，例如 (25.0375, 121.5637)。
      - None
        查不到或發生錯誤時回傳 None。
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _coords_by_city_sync, city_name)


@lru_cache(maxsize=1024)
def get_time_zone_by_city(city_name: str) -> Optional[str]:
    """
    由城市名稱取得 IANA 時區字串（例如 "Asia/Taipei"）。
    作法：
      1) 先用「同步 + 快取」的 _coords_by_city_sync(city) 取得經緯度
      2) 再用 TimezoneFinder 依座標推回 IANA 時區（純本地運算，無網路）
    回傳：
      - 時區字串（如 "Asia/Taipei"）
      - 查不到或發生錯誤時回 None
    備註：
      - 這裡選擇同步函式是因為第二步為本地計算且非常快；
        第一階段查座標已由 LRU 快取保護，多數情況不會重打外部服務。
    """
    coords = _coords_by_city_sync(city_name)
    if not coords:
        return None
    lat, lng = coords
    try:
        # 依序嘗試三種方法，提高命中率：
        # - timezone_at：標準判斷，點位落在時區多邊形內
        # - certain_timezone_at：更嚴格/更慢的確認（邊界情形）
        # - closest_timezone_at：都找不到時取最近時區（海上或邊界附近）
        return (_tf.timezone_at(lat=lat, lng=lng)
                or _tf.certain_timezone_at(lat=lat, lng=lng)
                or _tf.closest_timezone_at(lat=lat, lng=lng))
    except Exception as e:
        print(f"[get_time_zone_by_city] error: {e}")
        return None
