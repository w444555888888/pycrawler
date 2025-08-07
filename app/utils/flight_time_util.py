from datetime import datetime, timedelta
from app.utils.timezone import get_time_zone_by_city
from dateutil import tz


def calculate_arrival_date(
    departure_date: datetime,
    duration_min: int,
    dep_city: str,
    arr_city: str
) -> datetime:
    """
    根據出發時間與城市資訊計算抵達城市當地的 UTC 時間
    :param departure_date: 出發地的當地時間（無時區）
    :param duration_min: 飛行時間（分鐘）
    :param dep_city: 出發城市
    :param arr_city: 抵達城市
    :return: datetime（轉為 UTC）
    """
    dep_tz_str = get_time_zone_by_city(dep_city)
    arr_tz_str = get_time_zone_by_city(arr_city)

    if not dep_tz_str or not arr_tz_str:
        raise ValueError(f"Invalid timezone: {dep_city} or {arr_city}")

    dep_tz = tz.gettz(dep_tz_str)
    arr_tz = tz.gettz(arr_tz_str)

    # 將 departure_date 視為出發城市當地時間
    dep_dt_local = departure_date.replace(tzinfo=dep_tz)
    dep_utc = dep_dt_local.astimezone(tz.UTC)

    # 加上飛行時間
    arrival_utc = dep_utc + timedelta(minutes=duration_min)

    # 轉換成抵達城市當地時間，再轉為 UTC 存儲
    arrival_local = arrival_utc.astimezone(arr_tz)
    return arrival_local.astimezone(tz.UTC)