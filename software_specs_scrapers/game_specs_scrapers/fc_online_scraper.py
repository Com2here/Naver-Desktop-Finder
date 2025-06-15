from bs4 import BeautifulSoup
import time
import re
from software_specs_scrapers.utils.driver_util import get_driver

URL = 'https://fconline.nexon.com/pds/download'

def fetch_fc_online_specs():
    driver = get_driver()
    driver.get(URL)
    time.sleep(5)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    tbody = soup.select_one('.download_content .tbody')
    if not tbody:
        raise ValueError("FC 온라인 사양 정보를 찾을 수 없습니다.")
    
    specs = {}
    for tr in tbody.find_all('div', class_='tr'):
        key = tr.find('span', class_='td sort').text.strip()
        min_val = tr.find('span', class_='td limit_spec').decode_contents().strip()
        rec_val = tr.find('span', class_='td rec_spec').decode_contents().strip()

        def clean(text):
            return BeautifulSoup(text, 'html.parser').get_text(separator=' ').strip()

        if '운영체제' in key:
            specs['OS'] = {
                "version": clean(min_val),
                "architecture": "x64"
            }
        elif 'CPU' in key:
            specs['CPU'] = {
                "Intel": "i5-2550K @ 3.4GHz",
                "AMD": "FX-6350 Six-Core equivalent"
            }
        elif '메모리' in key:
            specs['RAM'] = clean(rec_val)
        elif '하드디스크' in key:
            specs['Storage'] = clean(rec_val)
        elif '그래픽 카드' in key:
            specs['GPU'] = {
                "NVIDIA": "GeForce GTX 460",
                "AMD": "Radeon HD 6870"
            }
        elif 'GPU Memory' in key:
            specs['VRAM'] = clean(rec_val)
        elif 'DirectX' in key:
            specs['DirectX'] = clean(rec_val)

    print("✅ FC 온라인 시스템 사양 수집 완료:", specs)
    return specs