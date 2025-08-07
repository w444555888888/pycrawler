from geopy.distance import geodesic
from app.utils.timezone import get_coords_by_city


async def calculate_flight_duration(departure_city: str, arrival_city: str) -> int:
    """
    根據兩城市的經緯度計算飛行時間（分鐘）
    假設平均速度為 900 km/h，使用 geopy 套件來取得球面直線距離
    """
    dep_coords = await get_coords_by_city(departure_city)
    arr_coords = await get_coords_by_city(arrival_city)

    if not dep_coords or not arr_coords:
        return None

    # 計算地球表面距離（公里）
    distance_km = geodesic(dep_coords, arr_coords).km

    # 飛機平均速度（km/h）
    speed_kmh = 900
    duration_hours = distance_km / speed_kmh

    return round(duration_hours * 60)  # 轉換成分鐘回傳