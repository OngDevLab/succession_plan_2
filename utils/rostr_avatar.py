from config.loader import CONFIG
import ssl
import certifi
from urllib.request import Request, urlopen
from functools import lru_cache

@lru_cache(maxsize=1024)
def get_rostr_avatar(employee_id):
    # Use URL from config
    photo_url = CONFIG['avatar']['url_template'].format(employee_id=employee_id)
    req = Request(photo_url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
 
    #certify ca cert
    context = ssl.create_default_context(cafile=certifi.where())

    with urlopen(req, context=context) as response:
        img_data =  response.read()

    return img_data
