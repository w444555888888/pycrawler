from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from typing import Optional, Tuple

geolocator = Nominatim(user_agent="flight_app")  # 請使用唯一 user_agent 名稱
tf = TimezoneFinder()

async def get_coords_by_city(city_name: str) -> Optional[Tuple[float, float]]:
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"[get_coords_by_city] error: {e}")
    return None

def get_time_zone_by_city(city_name: str) -> Optional[str]:
    try:
        location = geolocator.geocode(city_name)
        if location:
            timezone_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)
            return timezone_str
    except Exception as e:
        print(f"[get_time_zone_by_city] error: {e}")
    return None