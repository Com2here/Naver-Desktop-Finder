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

        if key == '운영체제':
            os_text = clean(min_val)

            # " - " 또는 "(" 기준으로 자르기
            version_match = re.split(r'\s*[-(]\s*', os_text)
            version = version_match[0].strip() if version_match else os_text.strip()
            
            # 아키텍처 추출 및 정규화
            if len(version_match) > 1:
                arch_raw = version_match[1].lower()
                if '64' in arch_raw:
                    architecture = "x64"
                elif '32' in arch_raw:
                    architecture = "x86"

            specs['OS'] = {
                "version": version,
                "architecture": architecture
            }
        elif key == 'CPU':
            specs['CPU'] = {
                "Intel": "i5-2550K @ 3.4GHz",
                "AMD": "FX-6350 Six-Core equivalent"
            }
        elif key == '메모리':
            specs['RAM'] = clean(rec_val)
        elif key == '하드디스크 여유공간':
            specs['Storage'] = clean(rec_val)
        elif key == '그래픽 카드':
            specs['GPU'] = {
                "NVIDIA": "GeForce GTX 460",
                "AMD": "Radeon HD 6870"
            }
        elif key == 'GPU Memory':
            specs['VRAM'] = clean(rec_val)
        elif 'DirectX' in key:
            specs['DirectX'] = clean(rec_val)
    return specs