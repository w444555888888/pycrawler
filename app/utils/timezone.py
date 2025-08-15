# utils/timezone.py
from __future__ import annotations
from typing import Optional, Tuple
from functools import lru_cache
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import asyncio



# 建立單例（全域共用，避免重複初始化）
_geolocator = Nominatim(user_agent="flight_app/1.0 (contact: you@example.com)", timeout=5)
_tf = TimezoneFinder()


@lru_cache(maxsize=1024)
def _coords_by_city_sync(city_name: str) -> Optional[Tuple[float, float]]:
    """同步版：查城市座標（帶快取），不得在事件迴圈中直接呼叫。"""
    if not city_name:
        return None
    try:
        loc = _geolocator.geocode(city_name, exactly_one=True)
        if not loc:
            return None
        return (loc.latitude, loc.longitude)
    except Exception as e:
        print(f"[get_coords_by_city] geocode error: {e}")
        return None

async def get_coords_by_city(city_name: str) -> Optional[Tuple[float, float]]:
    """非阻塞：把同步 geocode 丟到執行緒池跑。"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _coords_by_city_sync, city_name)


@lru_cache(maxsize=1024)
def get_time_zone_by_city(city_name: str) -> Optional[str]:
    """用座標推 IANA 時區（離線演算；帶快取）。"""
    coords = _coords_by_city_sync(city_name)
    if not coords:
        return None
    lat, lng = coords
    try:
        return (_tf.timezone_at(lat=lat, lng=lng)
                or _tf.certain_timezone_at(lat=lat, lng=lng)
                or _tf.closest_timezone_at(lat=lat, lng=lng))
    except Exception as e:
        print(f"[get_time_zone_by_city] error: {e}")
        return None
