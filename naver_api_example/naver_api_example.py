# 네이버 쇼핑 검색 API 예제
import os
import urllib.request
import urllib.parse
import json
import re
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 사용자 예산 설정
USER_BUDGET = 1200000  # 120만 원
# 검색어 설정
search_query = "RTX 5060 5600"

# 네이버 API 인증 정보
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# 검색어 인코딩
encText = urllib.parse.quote(search_query)
url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&exclude=rental"  # JSON 결과

# 요청 생성
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

# 요청 실행
response = urllib.request.urlopen(request)
rescode = response.getcode()

if rescode == 200:
    response_body = response.read()
    decoded_data = response_body.decode('utf-8')

    # JSON 파일로 저장
    try:
        json_data = json.loads(decoded_data)
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print("✅ 결과가 result.json 파일로 저장되었습니다.")
        items = json_data.get("items", [])

        seen_ids = set()
        filtered_items = []
        excluded_items = []

        for item in items:
            reason = None

            # 조건 1: category1 == "디지털/가전"
            if item.get("category1") != "디지털/가전":
                reason = "category1이 디지털/가전이 아님"

            # 조건 2: category2 == "PC"
            if item.get("category2") != "PC":
                reason = "category2가 PC가 아님"

            # 조건 3: 가격이 사용자 예산 이하인지 확인
            try:
                price = int(item.get("lprice", "0"))
            except ValueError:
                continue
            if price > USER_BUDGET:
                reason = "가격이 사용자 예산을 초과함"

            # 조건 4: 중복된 상품 ID 제거
            product_id = item.get("productId")
            if product_id in seen_ids:
                reason = "중복된 productId"

            if reason:
                # 필터링된 항목 저장
                excluded_items.append({
                    "title": re.sub(r"<.*?>", "", item.get("title", "")),
                    "link": item.get("link"),
                    "image": item.get("image"),
                    "lprice": item.get("lprice"),
                    "mallName": item.get("mallName"),
                    "reason": reason
                })
                continue

            # ✅ 사용자에게 보여줄 정보 구성
            seen_ids.add(product_id)
            clean_title = re.sub(r"<.*?>", "", item.get("title", ""))
            filtered_items.append({
                "title": clean_title,
                "link": item.get("link"),
                "image": item.get("image"),
                "lprice": price,
                "mallName": item.get("mallName"),
            })
            
        # 결과를 JSON 파일로 저장
        with open("filtered_result.json", "w", encoding="utf-8") as f:
            json.dump(filtered_items, f, indent=4, ensure_ascii=False)
        with open("excluded_result.json", "w", encoding="utf-8") as f:
            json.dump(excluded_items, f, indent=4, ensure_ascii=False)

        print(f"✅ 필터링된 {len(filtered_items)}개의 상품이 'filtered_result.json'에 저장되었습니다.")
        print(f"⚠️ 제외된 {len(excluded_items)}개 상품이 'excluded_result.json'에 저장되었습니다.")

    except json.JSONDecodeError as e:
        print(f"❌ JSON 디코딩 오류: {e}")

else:
    print("Error Code:" + str(rescode))