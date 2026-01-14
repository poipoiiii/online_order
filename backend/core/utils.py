import requests
from django.conf import settings

def get_lat_lng(address):
    """
    使用百度地图 Web 服务 API 将地址转换为经纬度
    """
    ak = getattr(settings, 'BAIDU_MAP_AK', None)
    if not ak:
        return 0.0, 0.0
    
    url = 'https://api.map.baidu.com/geocoding/v3/'
    params = {
        'address': address,
        'output': 'json',
        'ak': ak
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get('status') == 0:
            location = data['result']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding failed: {data}")
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return 0.0, 0.0
