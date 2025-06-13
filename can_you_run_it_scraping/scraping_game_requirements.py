from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

def parse_requirements_with_soup(html):
    soup = BeautifulSoup(html, "html.parser")
    req_dict = {}
    li_elements = soup.select("li")

    for li in li_elements:
        strong = li.find("strong")
        if strong:
            key = strong.text.strip().upper()
            strong.extract()
            value = li.text.strip().lstrip(":").strip()
            req_dict[key] = value

    return req_dict

def get_first_row_div_after(element):
    siblings = element.find_elements(By.XPATH, "following-sibling::div[contains(@class, 'row')]")
    if siblings:
        return siblings[0]
    else:
        raise Exception("다음 형제 중 row 클래스를 가진 div를 찾을 수 없습니다.")

def scrape_game_requirements(game_name):
    print("[1] 크롬 드라이버 옵션 설정 중...")
    options = Options()
    # options.add_argument("--headless")  # 브라우저 창 없이 실행하려면 주석 해제
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    })

    driver_path = "/opt/homebrew/bin/chromedriver"
    service = Service(driver_path)

    print("[2] 크롬 드라이버 실행 중...")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("[3] 웹사이트 접속 중: https://www.systemrequirementslab.com/cyri")
        driver.get("https://www.systemrequirementslab.com/cyri")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-repo-ts-control"))
        )

        print(f"[4] 게임명 '{game_name}' 검색창 대기 중...")
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-repo-ts-control"))
        )
        print("[5] 검색창에 게임명 입력 중...")
        search_input.clear()
        search_input.send_keys(game_name)

        first_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.option.active"))
        )
        driver.execute_script("arguments[0].click();", first_item)

        print("[6] 'Can You Run It?' 버튼 대기 중...")
        run_it_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "button-cyri-bigblue"))
        )
        print("[7] 버튼 클릭 중...")
        driver.execute_script("arguments[0].click();", run_it_btn)

        print("[8] 결과 섹션 대기 중...")
        headers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h2"))
        )

        target_min_h2 = None
        target_rec_h2 = None

        for h in headers:
            text = h.text.strip().lower()
            if "minimum" in text:
                target_min_h2 = h
            elif "recommended" in text:
                target_rec_h2 = h

        if not target_min_h2 or not target_rec_h2:
            raise Exception("필요한 h2 태그를 찾을 수 없습니다.")

        print("[9] 최소 사양 파싱 중...")
        min_req_div = get_first_row_div_after(target_min_h2)
        min_html = min_req_div.get_attribute("innerHTML")
        min_requirements = parse_requirements_with_soup(min_html)

        print("[10] 권장 사양 파싱 중...")
        rec_req_div = get_first_row_div_after(target_rec_h2)
        rec_html = rec_req_div.get_attribute("innerHTML")
        rec_requirements = parse_requirements_with_soup(rec_html)

        result = {
            "game": game_name,
            "minimum_requirements": min_requirements,
            "recommended_requirements": rec_requirements
        }

        print("[11] 사양 정보 수집 완료")
        return result

    finally:
        print("[12] 크롬 드라이버 종료 중...")
        driver.quit()

if __name__ == "__main__":
    game = "League of Legends"
    print(f"[0] '{game}' 게임 사양 정보 스크래핑 시작")
    data = scrape_game_requirements(game)

    filename = f"{game}_requirements.json"
    print(f"[13] 결과를 {filename} 파일로 저장 중...")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"[14] '{filename}' 에 저장 완료.")
