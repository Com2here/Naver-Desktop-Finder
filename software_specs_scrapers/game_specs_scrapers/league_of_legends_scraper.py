from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re

URL = 'https://support-leagueoflegends.riotgames.com/hc/ko/articles/201752654-%EC%B5%9C%EC%86%8C-%EB%B0%8F-%EA%B6%8C%EC%9E%A5-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EC%82%AC%EC%96%91-%EB%A6%AC%EA%B7%B8-%EC%98%A4%EB%B8%8C-%EB%A0%88%EC%A0%84%EB%93%9C'

def parse_key_value_p_tags(td_tag):
    result = {}
    p_tags = td_tag.find_all('p')
    for p in p_tags:
        text = p.get_text(strip=True)
        if ':' in text:
            key, val = text.split(':', 1)
            result[key.strip()] = val.strip()
    return result

def fetch_league_of_legends_specs():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 크롬드라이버 경로를 환경에 맞게 수정하세요
    service = Service('/opt/homebrew/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    time.sleep(5)  # 페이지 로딩 대기 (필요시 조절)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    specs_table = soup.find('table')
    if not specs_table:
        raise ValueError("문서 내에서 테이블을 찾을 수 없습니다.")

    specs = {}
    rows = specs_table.find_all('tr')
    for row in rows[1:]:  # 첫 행은 헤더라 건너뜀
        cols = row.find_all('td')
        if len(cols) >= 3:
            key = cols[0].text.strip()
            value_cell = cols[2]

            if key == 'CPU':
                result = parse_key_value_p_tags(value_cell)
                specs['CPU'] = result
            elif key == 'CPU 기능':
                specs['CPUFeatures'] = value_cell.text.strip()
            elif key == 'GPU':
                result = parse_key_value_p_tags(value_cell)
                specs['GPU'] = result
            elif key == 'GPU 기능':
                specs['GPUFeatures'] = value_cell.text.strip()
            elif key == 'VRAM':
                specs['VRAM'] = value_cell.text.strip()
            elif key == '여유 저장 공간':
                specs['Storage'] = value_cell.text.strip()
            elif '운영 체제 버전' in key:
                if 'OS' not in specs:
                    specs['OS'] = {}

                version_parts = []
                notes_parts = []

                # 각 <p> 태그를 순회
                for p in value_cell.find_all('p'):
                    for content in p.contents:
                        if isinstance(content, str):
                            text = content.strip()
                            if text:
                                version_parts.append(text)
                        else:
                            notes_parts.append(content.get_text(strip=True))

                full_version_text = ' '.join(version_parts)
                # 괄호 및 이후 텍스트 제거 (예: "Windows 11 (TPM 2.0)" → "Windows 11")
                cleaned_version = re.sub(r'\s*\(.*?\)', '', full_version_text).strip()

                specs['OS']['version'] = cleaned_version
                if notes_parts:
                    specs['OS']['notes'] = ' '.join(notes_parts)
            elif key == '운영 체제 아키텍쳐':
                if 'OS' not in specs:
                    specs['OS'] = {}
                specs['OS']['architecture'] = value_cell.text.strip()
            elif key == 'RAM':
                specs['RAM'] = value_cell.text.strip()
            elif key == '권장 그래픽 설정':
                specs['RecommendedGraphicsSetting'] = value_cell.text.strip()
            elif key == '권장 해상도':
                specs['RecommendedResolution'] = value_cell.text.strip()
    
    return specs